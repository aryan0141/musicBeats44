from django.db import models
from django.contrib.auth.models import User
# from django.contrib.postgres.fields import ArrayField
from django_mysql.models import ListCharField

yearOfRelease = (
    ('2021','2021'),
    ('2020','2020'),
    ('2019','2019'),
    ('2018','2018'),
    ('2017','2017'),
    ('2016','2016'),
    ('2015', '2015'),
    ('2014', '2014'),
    ('2013', '2013'),
    ('2012', '2012'),
    ('2011', '2011'),
    ('2010', '2010'),
    ('2009', '2009'),
    ('2008', '2008'),
    ('2007', '2007'),
    ('2006', '2006'),
    ('2005', '2005'),
    ('2004','2004'),
    ('2003','2003'),
    ('2002','2002'),
    ('2001','2001'),
    ('2000','2000'),
    ('1995','1995'),
    ('1990','1990'),
    ('1985','1985'),
)

genre = (
    ('Album','Album'),
    ('Bollywood','Bollywood'),
    ('Hollywood','Hollywood'),
)

language = (
    ('Hindi','Hindi'),
    ('Engligh','English'),
    ('Rajasthani','Rajasthani'),
    ('Haryanvi', 'Haryanvi'),
    ('Punjabi','Punjabi')
)


tags = (
    ('Classical','Classical'),
    ('Romantic','Romantic'),
    ('Pop','Pop'),
    ('Rock','Rock'),
    ('Devotional','Devotional'),
    ('Bhajan', 'Bhajan'),
    ('Dance','Dance'),
    ('Disco','Disco'),
    ('Ghazal','Ghazal'),
    ('Qawwali','Qawwali'),
)

productionHouse = (
    ('T-Series','T-Series'),
    ('Sony Music','Sony Music'),
    ('Zee Music Company','Zee Music Company'),
    ('Unknown','Unknown')
)



# Create your models here.
class Song(models.Model):
    song_id = models.AutoField(primary_key=True)
    count = models.IntegerField(default=0)
    name = models.CharField(max_length=200)
    tags = models.CharField(choices=tags, max_length=20, default='Classical')
    genre = models.CharField(choices=genre, max_length=20, default='Album')
    language = models.CharField(choices=language, max_length=20, default='Hindi')
    year = models.CharField(choices=yearOfRelease, max_length=20, default='2021')
    singer1 = models.CharField(max_length=200)
    singer2 = models.CharField(max_length=200, default='')
    productionHouse = models.CharField(choices=productionHouse, max_length=20, default='Unknown')
    movie = models.CharField(max_length=500, default="")
    # tags = models.CharField(max_length=100)
    image = models.ImageField(upload_to="images")
    song = models.FileField(upload_to='songs')

    def __str__(self):
        return self.name

class History(models.Model):
    hist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music_id = models.CharField(max_length=10000000, default="")

    def __str__(self):
        return self.user.first_name

class LikedSong(models.Model):
    liked_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music_id = models.CharField(max_length=10000000, default="")

    def __str__(self):
        return self.user.first_name


class Playlist(models.Model):
    playlist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # music_ids = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    # music_id = models.CharField(max_length=10000000, default="")
    music_ids = ListCharField(base_field=models.CharField(max_length=100), size=100, max_length=(100 * 101))
    playlist_name = models.CharField(max_length=10000000, default="")
    likes = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    plays = models.IntegerField(default=0)

    def __str__(self):
        return self.user.first_name

class Singer(models.Model):
    singer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="images/Singer")
    
    def __str__(self):
        return self.name