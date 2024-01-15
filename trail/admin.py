from django.contrib import admin
from .models import User, TrailFile, Trail, PhotoFile, TrailMap, SavedTrail, FollowedUser

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username")

class TrailFileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "trail", "trail_file")

class TrailDetailAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "trail_name", "public", "upload_time")
    list_filter = ["user"]

class PhotoFileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "trail", "photo_file")    

class TrailMapAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "trail")    

class SavedTrailAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "trail")  

class FollowedUserAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "following")  


admin.site.register(User, UserAdmin)
admin.site.register(TrailFile, TrailFileAdmin)
admin.site.register(PhotoFile, PhotoFileAdmin)
admin.site.register(Trail, TrailDetailAdmin)
admin.site.register(TrailMap, TrailMapAdmin)
admin.site.register(SavedTrail, SavedTrailAdmin)
admin.site.register(FollowedUser, FollowedUserAdmin)
