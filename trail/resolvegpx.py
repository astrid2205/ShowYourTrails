from datetime import time, date
from io import BytesIO
import gpxpy
from django.contrib import messages
from PIL import Image, UnidentifiedImageError, ImageOps, ImageDraw
from django.core.files.base import ContentFile
from django.db.models import Sum

from .models import PhotoFile, TrailFile, Trail, TrailMap


def resolvegpx(trailfile):
    """ 
    Take a gpx file as input, get some data from the trail,
    and render a trail map to be embedded in the web application.
    Return the information in a dictionary.
    """
    fmap = trailfile.open()
    fparsed = gpxpy.parse(fmap)

    coordinates = []
    accu_dist = []
    elev = []
    distance_from_start = 0
    previous_point = None

    for track in fparsed.tracks:
        # Simplify the gpx trail to avoid overcalculation of elevation gain,
        # and to generate the map with better performance.
        track.simplify()
        for segment in track.segments:
            for point in segment.points:
                coordinates.append([point.latitude, point.longitude])
                if previous_point:
                    distance_from_start += point.distance_3d(previous_point)
                accu_dist.append(distance_from_start)
                elev.append(round(point.elevation, 2))
                previous_point = point
                
        start_time = track.get_time_bounds().start_time
        end_time = track.get_time_bounds().end_time
        distance = (track.get_moving_data().moving_distance + track.get_moving_data().stopped_distance) / 1000
        duration = track.get_duration()
        track.get_bounds
        trail_detail = {
            "trail_name": track.name,
            "distance": round(distance, 2), #km
            "average_speed": round((distance / duration * 3600), 2), # km/hr
            "sum_uphill": round(track.get_uphill_downhill().uphill, 0), # m
            "sum_downhill": round(track.get_uphill_downhill().downhill, 0), # m
            "start_altitude": round(track.get_location_at(start_time)[0].elevation, 0), # m
            "end_altitude": round(track.get_location_at(end_time)[0].elevation, 0), # m
            "highest_altitude": round(track.get_elevation_extremes().maximum, 0), # m
            "lowest_altitude": round(track.get_elevation_extremes().minimum, 0), # m
            "start_time": start_time, # datetime
            "end_time": end_time,  # datetime
            "duration": convert_sec_to_time(duration), # time
            "duration_in_sec": duration,
            "moving_time": convert_sec_to_time(track.get_moving_data().moving_time), # time
            "stop_time": convert_sec_to_time(track.get_moving_data().stopped_time), # time
            "distance_elevation": [accu_dist, elev], # m, m
            "coordinates": coordinates,
            "map_center": [track.get_center().latitude, track.get_center().longitude],
        }
    return trail_detail


def convert_sec_to_time(second):
    second = int(second)
    hr , min = divmod(second, 3600)
    min , sec = divmod(min, 60)
    return time(hour=hr, minute=min, second=sec)


def save_new_photos(request, trail):
    photos = request.FILES.getlist("photo_files")
    for photo in photos:
        try:
            p = Image.open(photo)
            p.verify()
            thumb_photo = process_trail_photo(photo)
            compressed_photo = compress_trail_photo(photo)
            new_photo = PhotoFile()
            new_photo.fill_in_details({"user": request.user, "trail": trail})
            new_photo.photo_file.save(f"{photo.name}", compressed_photo, save=False)
            new_photo.thumbnail_file.save(f"thumb_{photo.name}", thumb_photo, save=False)
            new_photo.save()
        except (FileNotFoundError, UnidentifiedImageError, ValueError, TypeError) as err:
            messages.warning(request, f"{err}")


def process_trail_photo(image):
    image = crop_into_rectangle(image)
    image = create_thumbnail(image)
    return convert_to_file_instance(image)


def compress_trail_photo(image):
    image = compress_photo(image)
    return convert_to_file_instance(image)


def process_profile_photo(image):
    image = crop_into_rectangle(image)
    profile_photo = convert_to_file_instance(image)
    small_img = create_profile_thumbnail(image)
    profile_photo_thumb = convert_to_file_instance(small_img, "PNG")
    return profile_photo, profile_photo_thumb


def create_profile_thumbnail(image):
    new_width = min(image.size)*3
    mask = Image.new('L', (new_width, new_width), 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + (new_width, new_width), fill=255)
    mask = mask.resize(image.size, Image.LANCZOS)
    image.putalpha(mask)
    image.thumbnail((200,200))
    return image


def create_thumbnail(image, format="JPEG"):
    """
    Create a 200px * 200px thumbnail from input image.
    """
    width, height = image.size
    if width > 200 and height > 200:
        image.thumbnail((200, 200))
    return image


def compress_photo(image, format="JPEG"):
    """
    Reduce file size of the input image.
    """
    image = Image.open(image)

    # If the image has orientation
    image = ImageOps.exif_transpose(image)
    
    width, height = image.size
    if width > 1000 or height > 1000:
        if width < height:
            width = 1000 * width / height
            height = 1000
        else:
            height = 1000 * height / width
            width = 1000
    image.thumbnail((width, height))
    return image


def convert_to_file_instance(image, format='JPEG'):
    """Convert the PIL Image instance into a File instance (so it can be saved into Django ImageField)"""
    thumb_io = BytesIO()
    image.save(thumb_io, format)
    thumb_file = ContentFile(thumb_io.getvalue())
    return thumb_file


def crop_into_rectangle(image):
    image = Image.open(image)

    # If the image has orientation
    image = ImageOps.exif_transpose(image)
    
    # Crop the image into rectangle
    width, height = image.size
    if width > height:
        left = (width - height) / 2
        top = 0
        right = (height + width) / 2
        bottom = height
    else:
        left = 0
        top = (height - width) / 2
        right = width
        bottom = (height + width) / 2
    image = image.crop((left, top, right, bottom))
    return image


def save_new_trail(user, trail_name, trail_detail):
    new_trail = Trail()
    new_trail.fill_in_details(trail_detail)
    new_trail.user = user
    new_trail.trail_name = trail_name
    new_trail.save()
    return new_trail


def save_new_trail_file(user, trail, file):
    new_trail_file = TrailFile()
    new_trail_file.user = user
    new_trail_file.trail = trail
    new_trail_file.trail_file = file
    new_trail_file.save()


def save_new_trail_map(user, trail, trail_detail):
    new_trail_map = TrailMap()
    new_trail_map.user = user
    new_trail_map.trail = trail
    new_trail_map.coordinates = trail_detail["coordinates"]
    new_trail_map.dist_elev = trail_detail["distance_elevation"]
    new_trail_map.map_center = trail_detail["map_center"]
    new_trail_map.save()


def calc_stats(user, filter):
    if filter == 'all':
        trails = user.all_trails.all()
    elif filter == 'month':
        trails = user.all_trails.filter(start_time__month=date.today().month, start_time__year=date.today().year)
    elif filter == 'year':
        trails = user.all_trails.filter(start_time__year=date.today().year)
    else:
        return 'Invalid filter'
    
    trail_num = trails.count()
    stats = {'count': trail_num}

    if trail_num:
        if filter == 'all':
            biggest_climb = trails.order_by('-sum_uphill')[0]
            longest_trail = trails.order_by('-distance')[0]
            stats.update({
                'biggest_climb': {'id': biggest_climb.id, 'elev': biggest_climb.sum_uphill},
                'longest_trail': {'id': longest_trail.id, 'dist': longest_trail.distance}
            })
        stats.update(trails.aggregate(
            sum_dur=Sum("duration_in_sec"), 
            sum_dist=Sum("distance"), 
            sum_uphill=Sum("sum_uphill")))
        
        hours = stats['sum_dur'] // 3600
        mins = (stats['sum_dur'] % 3600) // 60
        stats['sum_dur'] = {"hours": hours, "mins": mins}
    else:
        stats.update(sum_dur={"hours": 0, "mins": 0}, sum_dist=0, sum_uphill=0)
    
    return stats

def show_stats(user):
    return {
        'month': calc_stats(user, 'month'),
        'year': calc_stats(user, 'year'),
        'all': calc_stats(user, 'all'),
    }