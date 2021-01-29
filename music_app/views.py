from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Song, History, LikedSong, Singer
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.db.models import Case, When
import json
import random
# Create your views here.


def history(request):
    recentSongs = History.objects.filter(user=request.user)
    ids = []
    for i in recentSongs:
        ids.append(i.music_id)
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    recentSongs = list(Song.objects.filter(song_id__in=ids).order_by(preserved))
    return render(request, 'history.html', {'history': recentSongs})

def allSongs(request):
    allSongs = list(Song.objects.all())
    return render(request, 'allSongs.html', {'allSongs': allSongs})


def singerpost(request, id):
    singer = Singer.objects.filter(singer_id=id).first()
    singerSongs = Song.objects.filter(singer1=singer.name).all()
    # singerSongs2 = Song.objects.filter(singer2=singer.name).all()
    # singerSongs = singerSongs1+singerSongs2
    # print(singerSongs)
    return render(request, 'singerpost.html', {'singerSongs': singerSongs, 'singer':singer})



def index(request):
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
    singers = list(Singer.objects.all())[:10]
    # print(singers[0].image)
    user = request.user
    if user.is_authenticated:
        recentSongs = History.objects.filter(user=user)
        ids = []
        for i in recentSongs:
            ids.append(i.music_id)
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
        recentSongs = list(Song.objects.filter(song_id__in=ids).order_by(preserved))
        recentSongs = recentSongs[:15]
        # print(recentSongs[0].movie)
        return render(request, "index.html", {'trendingSongs':trendingSongs, 'singers':singers, 'recentSongs':recentSongs, 'newRealeases':newRealeases})
    else:
        return render(request, "index.html", {'trendingSongs':trendingSongs, 'singers':singers, 'newRealeases':newRealeases})

def likesong(request):
    # print("Request Submitted Successfully!!!")
    user = request.user
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






def songpost(request, id):
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
                                            'isLiked':isLiked, 'isAlbum':isAlbum, 'recommendedSongs':finalRecommendedSongs[:5]})
    # return redirect("/")


def login(request):
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

def signup(request):
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
            user.save()
            messages.info(request,"User successfully created!")
            # print("User Created")
            return redirect("/")
    else:
        messages.info(request,"Password not matching!")
        # print("Password Not Match")
        return redirect("/")

def logout(request):
    auth.logout(request)
    messages.info(request,"User successfully Logged Out!")
    return redirect('/')
