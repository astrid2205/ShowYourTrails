from .models import User, Trail, PhotoFile, TrailFile, TrailMap, SavedTrail, FollowedUser
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    all_trails = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    following = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    followed_by = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'all_trails', 'following', 'followed_by']


class TrailSerializer(serializers.ModelSerializer):
    trail_map = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    photo_files = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Trail
        fields = '__all__'


class PhotoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoFile
        fields = '__all__'


class TrailFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TrailFile
        fields = '__all__'


class TrailMapSerializer(serializers.ModelSerializer):
    trail = TrailSerializer()

    class Meta:
        model = TrailMap
        fields = '__all__'


class SavedTrailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedTrail
        fields = '__all__'

        
class FollowedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowedUser
        fields = '__all__'        