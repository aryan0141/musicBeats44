# Generated by Django 2.2.5 on 2021-01-22 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music_app', '0012_song_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]
