import re
import requests
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
# from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib import messages
from rest_framework import permissions, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import SavedTrail, Trail, TrailMap, FollowedUser, User
from .forms import NewUserForm, TrailNameForm, TrailDescriptionForm, PasswordChange_Form
from .resolvegpx import *
from .permissions import IsOwnerOrReadOnly
from .serializers import FollowedUserSerializer, SavedTrailSerializer, TrailFileSerializer, TrailSerializer, UserSerializer, TrailMapSerializer, PhotoFileSerializer


def index(request):
    """
    Redirect to user dashboard if the user is logged in, 
    otherwise show index page with some introduction.
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("dashboard"))
    return render(request, "trail/index.html")


def login_view(request):
    """
    Login the user.
    Show login form if the user is not logged in, 
    otherwise redirect to user dashboard.
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f"Welcome, {username}")
            return HttpResponseRedirect(reverse("dashboard"))
        else:
            messages.error(request, "Invalid Credentials.")
            return render(request, "trail/login.html")

    elif request.user.is_authenticated:
        return HttpResponseRedirect(reverse("dashboard"))

    else:
        return render(request, "trail/login.html")


@login_required
def logout_view(request):
    """
    Log out the user.
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    Register the user.
    """
    # Handles post request and register the user
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You have registered successfully! Sign in to continue.")
            return HttpResponseRedirect(reverse("login"))
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect(reverse("register"))
    
    # Show register form
    else:
        form = NewUserForm()
        return render(request, "trail/register.html", {"form": form})


# TODO: 不同排列順序，search keyword，一次不要顯示太多
@login_required
def dashboard(request):
    """
    Show all the trails the user uploaded.
    """
    all_trails = request.user.all_trails.all().order_by("-upload_time")
    return render(request, "trail/dashboard.html", {"all_trails": all_trails})


def view_profile(request, user_id):
    """
    Show the user profile of the requested user.
    """
    trail_user = get_object_or_404(User, id=user_id)
    all_trails = Trail.objects.filter(user=user_id).order_by("-id")
    following_num = len(trail_user.following.all())
    followers_num = len(trail_user.followed_by.all())
    stats = show_stats(trail_user)
    user_followed = False
    if request.user.is_authenticated:
        try:
            user_followed = FollowedUser.objects.get(user=request.user, following=trail_user)
        except FollowedUser.DoesNotExist:
            pass            

    context = {
        "all_trails": all_trails, 
        "trail_user": trail_user,
        "following_num": following_num,
        "followers_num": followers_num,
        "user_followed": user_followed,
        "stats": stats
        }
    return render(request, "trail/profile.html", context)


@login_required
def upload(request):
    """
    Handles uploading of trail gpx file.
    """  
    # Upload files
    if request.method == "POST":
        # Get the gpx file from use upload
        try:
            file = request.FILES.get("trail_file")
        except Exception as error:
            messages.warning(request, f"{error}")
            return HttpResponseRedirect(reverse("upload"))
        
        # Parse gpx file
        try:
            trail_detail = resolvegpx(file)
        except Exception as error:
            messages.warning(request, f"We cannot analyse your trail. Check your file again.")
            return HttpResponseRedirect(reverse("upload"))

        # Save the parsed trail to the database
        user = request.user
        trail_name = re.search("(.*).gpx", file.name).group(1)
        trail = save_new_trail(user, trail_name, trail_detail)
        save_new_trail_file(user, trail, file)
        save_new_trail_map(user, trail, trail_detail)

        return HttpResponseRedirect(reverse("edit", args=(trail.id,)))

    # Show upload file form
    else:
        return render(request, "trail/upload.html")


class TrailListViews(generic.ListView):
    """
    Display all the trails set to public (for users to explore others' trails).
    """
    context_object_name = "all_trails"
    template_name = "trail/trails.html"

    def get_queryset(self):
        return Trail.objects.filter(public=True).order_by("-upload_time")
    

def explore(request):
    """
    Render the html file for exploring trails using the map.
    """
    coords = ''
    return render(request, "trail/explore.html", {"coords": coords})

    
@login_required
def view_saved_trails(request):
    """
    Display all the trails the user saved.
    """
    trail_id_sets = SavedTrail.objects.filter(user=request.user).values('trail')
    all_trails = Trail.objects.filter(id__in=trail_id_sets)
    return render(request, "trail/saved_trails.html", {"all_trails": all_trails})

    
# TODO: Share in social media/download gpx
def view_trail(request, trail_id):
    """
    Show all the details of the requested trail.
    """
    trail = get_object_or_404(Trail, id=trail_id)
    if not trail.public and trail.user != request.user:
        raise Http404("Trail does not exist")
    photos = trail.photo_files.all()
    trail_saved = False
    if request.user.is_authenticated:
        try:
            trail_saved = SavedTrail.objects.get(user=request.user, trail=trail)
        except SavedTrail.DoesNotExist:
            pass
    return render(request, "trail/trail.html", {"trail": trail, "photos": photos, "trail_saved": trail_saved})


@login_required
def edit_trail(request, trail_id):
    """
    Handles editing of the requested trail.
    """
    # POST request: save the edited trail to Trail database
    if request.method == "POST":
        trail = get_object_or_404(Trail, id=trail_id)

        # Check if it is the correct user editing the correct trail
        if request.user != trail.user:
            messages.warning(request, "Invalid edit.")
            return HttpResponseRedirect(reverse("dashboard"))
        
        trail.trail_name = request.POST["trail_name"]
        trail.description = request.POST["description"]
        trail.public = False if "public" not in request.POST else True
        trail.save()
        
        save_new_photos(request, trail)

        return HttpResponseRedirect(reverse("trail", args=(trail_id, )))
    
    # Shows the edit view.
    else:
        trail = get_object_or_404(Trail, id=trail_id)

        # Check if it is the correct user editing the correct trail
        if request.user != trail.user:
            messages.warning(request, "Sorry, you are not allowed to access that page.")
            return HttpResponseRedirect(reverse("dashboard"))
        
        context = {
            "trail": trail, 
            "name_form": TrailNameForm(initial={
                "trail_name": trail.trail_name, 
                "public": trail.public
                }),
            "description_form": TrailDescriptionForm(initial={
                "description": trail.description
                }),
            "photos": trail.photo_files.all()
            }        
        return render(request, "trail/edit_trail.html", context)    


@login_required
def delete_trail(request, trail_id):
    """
    Deletes the requested trail.
    """
    trail = get_object_or_404(Trail, id=trail_id)
    if request.user != trail.user:
        messages.warning(request, "Sorry, you are not allowed to access that page.")
    else:
        trail.delete()
        messages.success(request, f"Trail {trail.trail_name} deleted.")
    return HttpResponseRedirect(reverse("dashboard"))


def following(request, user_id):
    """
    Show the users the requested user is following.
    """
    trail_user = get_object_or_404(User, id=user_id)
    following = trail_user.following.all()
    return render(request, "trail/following.html", {"trail_user": trail_user, "following": following})


def followers(request, user_id):
    """
    Show the requested user's follower.
    """
    trail_user = get_object_or_404(User, id=user_id)
    followers = trail_user.followed_by.all()
    return render(request, "trail/followers.html", {"trail_user": trail_user, "followers": followers})


@login_required
def edit_profile(request):
    """
    Allows user to edit user profile photo and password.
    """
    if request.method == "POST":
        if "profile_photo" in request.FILES:
            photo = request.FILES["profile_photo"]
            profile_photo, profile_photo_thumb = process_profile_photo(photo)
            request.user.profile_photo.save(f"profile_photo_{request.user.id}.jpeg", profile_photo, save=False)
            request.user.profile_photo_thumb.save(f"thumb_profile_photo_{request.user.id}.png", profile_photo_thumb, save=False)
            request.user.save()
        else:
            form = PasswordChange_Form(request.user, data=request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user) # dont logout the user.
                messages.success(request, "Password changed.")
        return HttpResponseRedirect(reverse("edit_profile"))
    else:        
        form = PasswordChange_Form(request.user)
        return render(request, "trail/edit_profile.html", {"form": form})
    

""" APIs """
def user_all_maps_api(request, user_id):
    """
    Return the coordinates of all trails of the requested user in
    json format, so the map can be drawn on the front-end.
    """
    all_trails = TrailMap.objects.filter(user=user_id, trail__public=True)
    return JsonResponse([trail.serialize() for trail in all_trails], safe=False)


def explore_maps_api(request):
    """
    Return the coordinates of maximum 10 trails within the bounds in
    json format, so the map can be drawn on the front-end.
    """
    lat_min, lat_max = float(request.GET.get('lat_min')), float(request.GET.get('lat_max'))
    lon_min, lon_max = float(request.GET.get('lon_min')), float(request.GET.get('lon_max'))
    all_trails = TrailMap.objects.filter(map_center__0__range=(lat_min, lat_max), \
                                         map_center__1__range=(lon_min, lon_max), trail__public=True)[:10]
    return JsonResponse([trail.serialize() for trail in all_trails], safe=False)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TrailViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trails to be viewed or edited.
    """
    queryset = Trail.objects.all()
    serializer_class = TrailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['user__username', 'trail_name']
    filterset_fields = ['user', 'public']


class TrailMapViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trail maps to be viewed or edited.
    """
    queryset = TrailMap.objects.all()
    serializer_class = TrailMapSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ['user', 'trail']


class PhotoFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trail photo files to be viewed or edited.
    """
    queryset = PhotoFile.objects.all()
    serializer_class = PhotoFileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ['user', 'trail']


class TrailFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trail files to be viewed or edited.
    """
    queryset = TrailFile.objects.all()
    serializer_class = TrailFileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ['user', 'trail']


class SavedTrailViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trails saved by the users to be viewed or edited.
    """
    queryset = SavedTrail.objects.all()
    serializer_class = SavedTrailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ['user', 'trail']


class FollowedUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows followers to be viewed or edited.
    """
    queryset = FollowedUser.objects.all()
    serializer_class = FollowedUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ['user', 'following']