from django.contrib import admin
from .models import Song, History, LikedSong, Singer, Playlist
# Register your models here.
admin.site.register(Song)
admin.site.register(History)
admin.site.register(LikedSong)
admin.site.register(Singer)
admin.site.register(Playlist)
