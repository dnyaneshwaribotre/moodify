from django.contrib import admin
from .models import Profile, Song, Playlist, PlaylistSong, Favorite, ListeningHistory, MoodHistory, UserInteraction
admin.site.register([Profile,Song,Playlist,PlaylistSong,Favorite,ListeningHistory,MoodHistory,UserInteraction])
