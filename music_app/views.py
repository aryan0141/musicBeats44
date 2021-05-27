from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Song, History, LikedSong, Singer, Playlist
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.db.models import Case, When
import json
import random
import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials
import os
# Create your views here.


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id='1ff69d94deb24751b4e1a55c9bf9301d',client_secret='05f6def4895641848da6cfeaa6afceef'))
myPlaylists = []

def searchResults(request):
    user = request.user
    myPlaylists = []
    if user.is_authenticated:
        # Extracting Playlists of the Authenticated User
        myPlaylists = list(Playlist.objects.filter(user=user))
    if request.method=="POST":
        data = request.POST["data"]
        # print(data)
        allSongs = Song.objects.all()
        songsFound = allSongs.filter(name__icontains=data)
        moviesFound = allSongs.filter(movie__icontains=data)
        songsFound = list(set(list(songsFound)+list(moviesFound)))[:6]
        
        allSingers = Singer.objects.all()
        singersFound = allSingers.filter(name__icontains=data)

        return render(request, 'searchResults.html', {'songsFound':songsFound, 'singersFound':singersFound, 'myPlaylists':myPlaylists})
    else:
        return redirect("/")

def history(request):
        user = request.user
        if user.is_authenticated:
            # Extracting Playlists of the Authenticated User
            myPlaylists = list(Playlist.objects.filter(user=user))
        if request.method=="POST":
            History.objects.filter(user=request.user).delete()
            message="Successful"
            # return redirect("/")
            return HttpResponse(json.dumps({'message': message})) 
        else:
            recentSongs = History.objects.filter(user=request.user)
            ids = []
            for i in recentSongs:
                ids.append(i.music_id)
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
            recentSongs = list(Song.objects.filter(song_id__in=ids).order_by(preserved))
            return render(request, 'history.html', {'history': recentSongs, 'myPlaylists':myPlaylists})

def allSongs(request):
    myPlaylists  = []
    user = request.user
    if user.is_authenticated:
        # Extracting Playlists of the Authenticated User
        myPlaylists = list(Playlist.objects.filter(user=user))
    try:
        allSongs = list(Song.objects.all())
        random.shuffle(allSongs)
        return render(request, 'allSongs.html', {'allSongs': allSongs, 'myPlaylists':myPlaylists})
    except:
        return redirect("/")

def singerpost(request, id):
    user = request.user
    myPlaylists  = []
    if user.is_authenticated:
        # Extracting Playlists of the Authenticated User
        myPlaylists = list(Playlist.objects.filter(user=user))
    # try:
    singer = Singer.objects.filter(singer_id=id).first()
    singerSongs = Song.objects.filter(singer1=singer.name).all()
    name = singer.name
    print(name)
    results = spotify.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    # if len(items) > 0:
        # artist = items[0]
        # print(artist['uri'])
        # print(artist['name'], artist['images'][0]['url'])
    results = spotify.artist_top_tracks(items[0]['uri'])
    final_result=results['tracks'][:10]
    items[0]['type'] = items[0]['type'].capitalize()
    for i in range (len(items[0]['genres'])):
        items[0]['genres'][i] = items[0]['genres'][i].title()
    # for track in results['tracks'][:10]:
        # print(track['name'])
    return render(request, 'singerpost.html', {'singerSongs': final_result, 'singer':items[0], 'myPlaylists':myPlaylists})

def createPlaylist(request):
    try:
        user = request.user
        if(user.is_authenticated):
            playlist_name = request.POST["playlist_name"]
            newPlaylist = Playlist(user = user, music_ids=[], playlist_name=playlist_name)
            newPlaylist.save()
            return redirect("/")
        else:
            return redirect("/")
    except:
        return redirect("/")

def myPlaylist(request, id):
        user = request.user
        if user.is_authenticated:
            # Extracting Playlists of the Authenticated User
            myPlaylists = list(Playlist.objects.filter(user=user))
        if(user.is_authenticated):
            if request.method=="POST":
                song_id = request.POST["music_id"]
                playlist = Playlist.objects.filter(playlist_id=id).first()
                if song_id in playlist.music_ids:
                    playlist.music_ids.remove(song_id)
                    playlist.plays-=1
                    playlist.save()
                message = "Successfull"
                print(message)
                return HttpResponse(json.dumps({'message': message})) 

            else:

                images = os.listdir("music_app/static/PlaylistImages")
                print(images)
                randomImagePath = random.choice(images)
                randomImagePath = "PlaylistImages/"+randomImagePath
                print(randomImagePath)

                currPlaylist = Playlist.objects.filter(playlist_id=id).first()
                music_ids = currPlaylist.music_ids
                playlistSongs = []
                recommendedSingers = []

                for music_id in music_ids:
                    song = Song.objects.filter(song_id=music_id).first()
                    
                    if Singer.objects.filter(name=song.singer1).exists():
                        singer1 = list(Singer.objects.filter(name=song.singer1))
                        recommendedSingers+=singer1
                    
                    if Singer.objects.filter(name=song.singer2).exists():
                        singer2 = list(Singer.objects.filter(name=song.singer2))
                        recommendedSingers+=singer2

                    random.shuffle(recommendedSingers)
                    recommendedSingers = list(set(recommendedSingers))[:6]
                    
                    playlistSongs.append(song)

                return render(request, "myPlaylist.html", {'playlistInfo':currPlaylist, 'playlistSongs':playlistSongs,
                                                            'myPlaylists':myPlaylists, 'recommendedSingers':recommendedSingers, 'randomImagePath':randomImagePath})

def deletePlaylist(request):
    if request.method=="POST":
        playlist_id = request.POST["playlist_id"]
        # print(playlist_id)
        Playlist.objects.filter(playlist_id=playlist_id).delete()
        messages.info(request,"Playlist Deleted")
        print("Playlist Deleted")
    return redirect("/")

def addSongToPlaylist(request):
    user = request.user
    if(user.is_authenticated):
        try:
            data = request.POST['data']
            ids = data.split("|")
            song_id = ids[0][2:]
            playlist_id = ids[1][2:]
            print(ids[0][2:], ids[1][2:])
            currPlaylist = Playlist.objects.filter(playlist_id=playlist_id).first()
            if song_id not in currPlaylist.music_ids:
                currPlaylist.music_ids.append(song_id)
                currPlaylist.plays = len(currPlaylist.music_ids)
                currPlaylist.save()
            return HttpResponse("Successfull")
        except:
            return redirect("/")
        # return redirect("/")
    else:
        return redirect("/")

def index(request):
    # try:
        user = request.user
        if user.is_authenticated:
            # Extracting Playlists of the Authenticated User
            myPlaylists = list(Playlist.objects.filter(user=user))

        allSongs = list(Song.objects.all())
        trendingSongs = list(Song.objects.all().exclude(movie='Album'))
        
        # New Realeases-
        sameMovie = []
        newRealeases = []
        for i in allSongs:
            if int(i.year)>=2019:
                if i.movie=='Album' or (i.movie not in sameMovie):
                    newRealeases.append(i)
                    sameMovie.append(i.movie)
        random.shuffle(newRealeases)
        newRealeases = newRealeases[:15]
        # print(newRealeases)
        del sameMovie
        
        # Trending Songs-
        random.shuffle(trendingSongs)
        trendingSongs = trendingSongs[:10]
        singers = list(Singer.objects.all())



        # Extracting Various Songs From Various Singers Using Spotify API
        songsFromVariousArtists = []
        random.shuffle(singers)
        for singer in singers[:5]:
            name = singer.name
            results = spotify.search(q='artist:' + name, type='artist')
            items = results['artists']['items']
            results = spotify.artist_top_tracks(items[0]['uri'])
            songsFromVariousArtists+=results['tracks'][:3]
        
        # songsFromVariousArtists = list(set(list(songsFromVariou

        # print(songsFromVariousArtists)
        random.shuffle(singers)
        singers = singers[:11]




        # print(singers[0].image)
        # user = request.user
        if user.is_authenticated:
            # Extracting Playlists of the Authenticated User
            myPlaylists = Playlist.objects.filter(user=user)
            recentSongs = History.objects.filter(user=user)
            ids = []
            for i in recentSongs:   
                ids.append(i.music_id)
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
            recentSongs = list(Song.objects.filter(song_id__in=ids).order_by(preserved))
            recentSongs = recentSongs[:15]
            # print(recentSongs[0].movie)
            return render(request, "index.html", {'trendingSongs':trendingSongs, 'singers':singers, 'newRealeases':newRealeases,
                            'songsFromVariousArtists':songsFromVariousArtists, 'recentSongs':recentSongs, 'myPlaylists':myPlaylists})
        else:
            return render(request, "index.html", {'trendingSongs':trendingSongs, 'singers':singers, 'newRealeases':newRealeases,
                                        'songsFromVariousArtists':songsFromVariousArtists})
    # except:
    #     return redirect("/")

def likesong(request):
    myPlaylists  = []
    try:
        # print("Request Submitted Successfully!!!")
        user = request.user
        if user.is_authenticated:
            # Extracting Playlists of the Authenticated User
            myPlaylists = list(Playlist.objects.filter(user=user))
        if(user.is_authenticated):
            if request.method=="POST":
                song_id = request.POST["music_id"]
                isPresent = False
                if LikedSong.objects.filter(user=user, music_id=song_id).exists():
                    isPresent = True

                if isPresent:
                    LikedSong.objects.filter(user=user, music_id=song_id).delete()
                    # print(f"Your song is removed from the liked song Id: {song_id}")
                else:
                    like = LikedSong(user = user, music_id = song_id)
                    like.save()
                    # print(f"Your song successfully added Id: {song_id}")
                message = "Successfull"
                return HttpResponse(json.dumps({'message': message})) 
            else:
                like = LikedSong.objects.filter(user=user)
                ids = []
                for i in like:
                    ids.append(i.music_id)
                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
                likedSongs = Song.objects.filter(song_id__in=ids).order_by(preserved)
                # print(recentSongs[0].movie)
                return render(request, "likedSong.html", {'likedSongs':likedSongs})
        else:
            # print("User is not authenticated")
            return redirect("/")
    except:
        return redirect("/")

def songpost(request, id):
    myPlaylists  = []
    user = request.user
    if user.is_authenticated:
        # Extracting Playlists of the Authenticated User
        myPlaylists = list(Playlist.objects.filter(user=user))
    try:
        song = Song.objects.filter(song_id=id).first()
        song.count+=1
        song.save()

        if song.movie=='Album':
            isAlbum = True
        else:
            isAlbum = False


        recommendedSongs = []
        song_tag = song.tags
        song_year = song.year
        if(song_tag=='Classical' or song_tag=='Romantic'):
            moreSongs = list(Song.objects.filter(tags='Classical').exclude(song_id=id))
            recommendedSongs+=moreSongs
            moreSongs = list(Song.objects.filter(tags='Romantic').exclude(song_id=id))
            recommendedSongs+=moreSongs
        
        if(song_tag=='Rock' or song_tag=='Pop' or song_tag=='Dance'):
            moreSongs = list(Song.objects.filter(tags='Rock').exclude(song_id=id))
            recommendedSongs+=moreSongs
            moreSongs = list(Song.objects.filter(tags='Pop').exclude(song_id=id))
            recommendedSongs+=moreSongs
            moreSongs = list(Song.objects.filter(tags='Dance').exclude(song_id=id))
            recommendedSongs+=moreSongs
            moreSongs = list(Song.objects.filter(tags='Disco').exclude(song_id=id))
            recommendedSongs+=moreSongs

        # Filter the songs with respect to their year
        finalRecommendedSongs = []
        for i in recommendedSongs:
            if(int(i.year)==int(song_year) or int(i.year)==int(song_year)-2 or int(i.year)==int(song_year)+2):
                finalRecommendedSongs.append(i)

        

        # This is to find all the singers of that particular movie PART1-
        recommendedSingers = []
        if Singer.objects.filter(name=song.singer1).exists():
            singer1 = list(Singer.objects.filter(name=song.singer1))
            recommendedSingers+=singer1
        if Singer.objects.filter(name=song.singer2).exists():
            singer2 = list(Singer.objects.filter(name=song.singer2))
            recommendedSingers+=singer2




        if(song.movie=='Album'):
            sameMovieSongs = list(Song.objects.filter(singer1=song.singer1).all().exclude(song_id=id))
            otherSongs = list(Song.objects.filter(tags=song.tags).all().exclude(song_id=id))
            random.shuffle(otherSongs)
            sameMovieSongs = sameMovieSongs[:2] + otherSongs[:3]
            sameMovieSongs = set(sameMovieSongs)
            sameMovieSongs = list(sameMovieSongs)

        else:
            sameMovieSongs = Song.objects.filter(movie=song.movie).all().exclude(song_id=id)


        newList = []
        for i in finalRecommendedSongs:
            if i not in sameMovieSongs:
                newList.append(i)
        # finalRecommendedSongs = list(set(sameMovieSongs).symmetric_difference(set(finalRecommendedSongs)))
        finalRecommendedSongs = newList
        random.shuffle(finalRecommendedSongs)



        # This is to find all the singers of that particular movie PART2- 
        for i in sameMovieSongs:
            if Singer.objects.filter(name=i.singer1).exists():
                singer1 = list(Singer.objects.filter(name=i.singer1))
                recommendedSingers+=singer1
            if Singer.objects.filter(name=i.singer2).exists():
                singer2 = list(Singer.objects.filter(name=i.singer2))
                recommendedSingers+=singer2
        for i in finalRecommendedSongs:
            if Singer.objects.filter(name=i.singer1).exists():
                singer1 = list(Singer.objects.filter(name=i.singer1))
                recommendedSingers+=singer1
            if Singer.objects.filter(name=i.singer2).exists():
                singer2 = list(Singer.objects.filter(name=i.singer2))
                recommendedSingers+=singer2
        recommendedSingers = list(set(recommendedSingers))
        # print(recommendedSingers)
        # print(song.name)
        isLiked = False
        user = request.user
        if user.is_authenticated:
            song_id = song.song_id
            if LikedSong.objects.filter(user=user, music_id=song_id).exists():
                isLiked=True
            
            if History.objects.filter(user=user, music_id=song_id).exists():
                History.objects.filter(user=user, music_id=song_id).delete()
            
            history = History(user=user, music_id = song_id)
            history.save()

        return render(request, 'songpost.html', {'song': song, 'sameMovieSongs': sameMovieSongs, 'recommendedSingers':recommendedSingers[:5], 
                                                'isLiked':isLiked, 'isAlbum':isAlbum, 'recommendedSongs':finalRecommendedSongs[:5], 'myPlaylists':myPlaylists})
    # return redirect("/")
    except:
        return redirect("/")

def login(request):
    try:
        username = request.POST.get("uname","default")
        password = request.POST.get("psw","default")

        user = auth.authenticate(username = username, password = password)
        if user is not None:
            auth.login(request,user)
            return redirect("/")

        else:
            messages.info(request,"Invalid Credentials!")
            # print("Invalid Credits.")
            return redirect("/")
    except:
        return redirect("/")

def signup(request):
    try:
        fname = request.POST.get("fname","default")
        lname = request.POST.get("lname","default")
        username = request.POST.get("username","default")
        email = request.POST.get("email","default")
        password = request.POST.get("psw","default")
        cpassword = request.POST.get("c_psw","default")
        if password==cpassword:
            if User.objects.filter(username = username).exists():
                messages.info(request,"Username already taken!")
                # print("Username Taken")
                return redirect("/")
            elif User.objects.filter(email = email).exists():
                messages.info(request,"Email already taken!")
                # print("Email Taken")
                return redirect("/")
            else:
                user = User.objects.create_user(username=username, email=email, password=password, first_name=fname, last_name=lname)
                messages.info(request,"User Created!")
                user.save()
                # print("User Created")
                user = auth.authenticate(username = username, password = password)
                auth.login(request,user)
                return redirect("/")
        else:
            messages.info(request,"Password not matching!")
            # print("Password Not Match")
            return redirect("/")
    except:
        return redirect("/")

def logout(request):
    try:
        auth.logout(request)
        messages.info(request,"User Logged Out!")
        return redirect('/')
    except:
        return redirect("/")