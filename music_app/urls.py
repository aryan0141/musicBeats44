from django.contrib import admin
from django.urls import path, include
from .import views
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import url
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('login', views.login, name="login"),
    path('signup', views.signup, name="signup"),
    path('logout', views.logout, name="logout"),
    path('likesong', views.likesong, name = "likesong"),
    path('allSongs', views.allSongs, name="allSongs"),
    path('history', views.history, name="history"),
    path('song/<int:id>', views.songpost, name='songpost'),
    path('album/<int:id>', views.singerpost, name='singerpost'),
    path('createPlaylist', views.createPlaylist, name='createPlaylist'),
    path('myPlaylist/<int:id>', views.myPlaylist, name='myPlaylist'),
    path('addSongToPlaylist', views.addSongToPlaylist, name='addSongToPlaylist'),
    path('deletePlaylist', views.deletePlaylist, name='deletePlaylist'),
    path('searchResults', views.searchResults, name='searchResults'),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    
    path('accounts/', include('allauth.urls')),
]
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
