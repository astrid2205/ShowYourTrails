from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    profile_photo = models.ImageField(upload_to="profilephoto/", blank=True)
    profile_photo_thumb = models.ImageField(upload_to="profilephoto/thumbnail/", blank=True)

class Trail(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="all_trails")
    trail_name = models.CharField(max_length=128)
    upload_time = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    average_speed = models.DecimalField(max_digits=10, decimal_places=2)
    sum_uphill = models.DecimalField(max_digits=10, decimal_places=2)
    sum_downhill = models.DecimalField(max_digits=10, decimal_places=2)
    start_altitude = models.DecimalField(max_digits=10, decimal_places=2)
    end_altitude = models.DecimalField(max_digits=10, decimal_places=2)
    highest_altitude = models.DecimalField(max_digits=10, decimal_places=2)
    lowest_altitude = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.TimeField()
    duration_in_sec = models.IntegerField()
    moving_time = models.TimeField()
    stop_time = models.TimeField()
    public = models.BooleanField()

    def __str__(self):
        return f"Trail {self.id}: {self.trail_name}"

    def fill_in_details(self, detail):
        self.distance = detail["distance"]
        self.average_speed = detail["average_speed"]
        self.sum_uphill = detail["sum_uphill"]
        self.sum_downhill = detail["sum_downhill"]
        self.start_altitude = detail["start_altitude"]
        self.end_altitude = detail["end_altitude"]
        self.highest_altitude = detail["highest_altitude"]
        self.lowest_altitude = detail["lowest_altitude"]
        self.start_time = detail["start_time"]
        self.end_time = detail["end_time"]
        self.duration = detail["duration"]
        self.duration_in_sec = detail["duration_in_sec"]
        self.moving_time = detail["moving_time"]
        self.stop_time = detail["stop_time"]
        self.public = False


class PhotoFile(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="all_photos")
    trail = models.ForeignKey("Trail", on_delete=models.CASCADE, related_name="photo_files")
    photo_file = models.ImageField(upload_to="trailphotos")
    thumbnail_file = models.ImageField(upload_to="trailphotos/thumbnail")

    def fill_in_details(self, detail):
        self.user = detail['user']
        self.trail = detail['trail']


class TrailFile(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="trail_files")
    trail = models.ForeignKey("Trail", on_delete=models.CASCADE, related_name="trail_file")
    trail_file = models.FileField(upload_to="trailfiles")


class TrailMap(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="trail_maps")
    trail = models.ForeignKey("Trail", on_delete=models.CASCADE, related_name="trail_map")
    coordinates = models.JSONField()
    dist_elev = models.JSONField()
    map_center = models.JSONField()

    def serialize(self):
        return {
            "id": self.id,
            "trail": {
                "id": self.trail.id,
                "trail_name": self.trail.trail_name,
                "distance": self.trail.distance,
                "duration": self.trail.duration,
                "sum_uphill": self.trail.sum_uphill},
            "coordinates": self.coordinates,
            "dist_elev": self.dist_elev,
            "map_center": self.map_center,
        }
    

class SavedTrail(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="trails_saved")
    trail = models.ForeignKey("Trail", on_delete=models.CASCADE, related_name="saved_by_user")


class FollowedUser(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followed_by")

    def __str__(self):
        return f"{self.user} is following {self.following}"