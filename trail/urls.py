from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'trails', views.TrailViewSet)
router.register(r'trailmaps', views.TrailMapViewSet)
router.register(r'photofiles', views.PhotoFileViewSet)
router.register(r'trailfiles', views.TrailFileViewSet)
router.register(r'savedtrails', views.SavedTrailViewSet)
router.register(r'followeduser', views.FollowedUserViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path("upload", views.upload, name="upload"),
    path("trails", views.TrailListViews.as_view(), name="showtrails"),
    path("explore", views.explore, name="explore"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("login", views.login_view, name="login"),
    path("accounts/login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("trail/<int:trail_id>/", views.view_trail, name="trail"),
    path("trail/<int:trail_id>/edit", views.edit_trail, name="edit"),
    path("trail/<int:trail_id>/delete", views.delete_trail, name="delete"),
    path("user/<int:user_id>/", views.view_profile, name="view_profile"),
    path("saved/", views.view_saved_trails, name="view_saved_trails"),
    path("user/<int:user_id>/following", views.following, name="following"),
    path("user/<int:user_id>/followers", views.followers, name="followers"),
    path("accounts/edit", views.edit_profile, name="edit_profile"),
    path("api/user_maps/<int:user_id>/", views.user_all_maps_api, name="user_all_maps_api"),
    path("api/explore_maps/", views.explore_maps_api, name="explore_maps_api"),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
