from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from .models import Profile, Song, Playlist, PlaylistSong, Favorite, ListeningHistory, MoodHistory, UserInteraction
User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta: model=User; fields=['id','username','email']
class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    class Meta: model=Profile; fields=['id','username','email','preferred_genres','preferred_languages','favorite_artists','preferred_mood','created_at','updated_at']; read_only_fields=['created_at','updated_at']
    def update(self, instance, validated_data):
        user_data=validated_data.pop('user', {})
        for key,val in user_data.items(): setattr(instance.user,key,val)
        if user_data: instance.user.save()
        return super().update(instance,validated_data)
class RegisterSerializer(serializers.Serializer):
    email=serializers.EmailField(); username=serializers.CharField(max_length=150); password=serializers.CharField(write_only=True,min_length=6)
    def validate_email(self,value):
        if User.objects.filter(email__iexact=value).exists(): raise serializers.ValidationError('An account with this email already exists.')
        return value
    def validate_username(self,value):
        if User.objects.filter(username__iexact=value).exists(): raise serializers.ValidationError('This username is already taken.')
        return value
class SongSerializer(serializers.ModelSerializer):
    era=serializers.CharField(read_only=True)
    class Meta: model=Song; fields='__all__'
class PlaylistSongSerializer(serializers.ModelSerializer):
    song=SongSerializer(read_only=True)
    class Meta: model=PlaylistSong; fields=['id','song','position','added_at']
class PlaylistSerializer(serializers.ModelSerializer):
    songs=serializers.SerializerMethodField(); song_ids=serializers.ListField(child=serializers.IntegerField(),write_only=True,required=False)
    song_count=serializers.IntegerField(read_only=True); total_duration=serializers.IntegerField(read_only=True)
    class Meta: model=Playlist; fields=['id','name','mood','emotion','energy_level','description','confidence','cover_gradient','song_count','total_duration','created_at','updated_at','songs','song_ids']
    def get_songs(self,obj): return SongSerializer([x.song for x in obj.playlist_songs.select_related('song')],many=True).data
    def create(self,validated_data):
        song_ids=validated_data.pop('song_ids',[]); playlist=Playlist.objects.create(user=self.context['request'].user,**validated_data)
        for pos,song_id in enumerate(song_ids):
            song=Song.objects.filter(id=song_id).first()
            if song:
                PlaylistSong.objects.get_or_create(playlist=playlist,song=song,defaults={'position':pos})
        return playlist
class FavoriteSerializer(serializers.ModelSerializer):
    song=SongSerializer(read_only=True); song_id=serializers.PrimaryKeyRelatedField(queryset=Song.objects.all(),source='song')
    class Meta: model=Favorite; fields=['id','song','song_id','created_at']
class HistorySerializer(serializers.ModelSerializer):
    song=SongSerializer(read_only=True); song_id=serializers.PrimaryKeyRelatedField(queryset=Song.objects.all(),source='song')
    class Meta: model=ListeningHistory; fields=['id','song','song_id','played_at','duration_played','completed']
class MoodHistorySerializer(serializers.ModelSerializer):
    class Meta: model=MoodHistory; fields=['id','input_text','detected_emotion','detected_mood','energy_level','confidence','created_at']; read_only_fields=['id','created_at']
class InteractionSerializer(serializers.ModelSerializer):
    song_id=serializers.PrimaryKeyRelatedField(queryset=Song.objects.all(),source='song')
    class Meta: model=UserInteraction; fields=['id','song_id','song','interaction_type','created_at']; read_only_fields=['id','created_at','song']
