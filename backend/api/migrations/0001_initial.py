from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("preferred_genres", models.JSONField(blank=True, default=list)),
                ("preferred_languages", models.JSONField(blank=True, default=list)),
                ("favorite_artists", models.JSONField(blank=True, default=list)),
                ("preferred_mood", models.CharField(default="chill", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Song",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(default="demo", max_length=32)),
                ("provider_track_id", models.CharField(blank=True, max_length=255)),
                ("title", models.CharField(max_length=255)),
                ("artist", models.CharField(max_length=255)),
                ("album", models.CharField(blank=True, max_length=255)),
                ("genre", models.CharField(db_index=True, default="pop", max_length=80)),
                ("language", models.CharField(db_index=True, default="english", max_length=40)),
                ("mood", models.CharField(db_index=True, default="chill", max_length=40)),
                ("emotion", models.CharField(default="neutral", max_length=40)),
                ("energy_level", models.CharField(db_index=True, default="medium", max_length=16)),
                ("duration", models.PositiveIntegerField(default=180)),
                ("image_url", models.URLField(blank=True)),
                ("external_url", models.URLField(blank=True)),
                ("preview_url", models.URLField(blank=True)),
                ("popularity_score", models.PositiveSmallIntegerField(db_index=True, default=50)),
                ("release_date", models.DateField(blank=True, null=True)),
                ("plays", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-popularity_score", "title"],
            },
        ),
        migrations.CreateModel(
            name="Playlist",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("mood", models.CharField(default="chill", max_length=40)),
                ("emotion", models.CharField(default="neutral", max_length=40)),
                ("energy_level", models.CharField(default="medium", max_length=16)),
                ("description", models.TextField(blank=True)),
                ("confidence", models.FloatField(default=0)),
                ("cover_gradient", models.CharField(default="linear-gradient(135deg, #1f2937, #374151)", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="playlists", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="PlaylistSong",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("position", models.PositiveIntegerField(default=0)),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("playlist", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="playlist_songs", to="api.playlist")),
                ("song", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.song")),
            ],
            options={"ordering": ["position"]},
        ),
        migrations.CreateModel(
            name="Favorite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("song", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favorited_by", to="api.song")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favorites", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ListeningHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("played_at", models.DateTimeField(auto_now_add=True)),
                ("duration_played", models.PositiveIntegerField(default=0)),
                ("completed", models.BooleanField(default=False)),
                ("song", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.song")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="listening_history", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-played_at"]},
        ),
        migrations.CreateModel(
            name="MoodHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("input_text", models.TextField()),
                ("detected_emotion", models.CharField(max_length=40)),
                ("detected_mood", models.CharField(max_length=40)),
                ("energy_level", models.CharField(default="medium", max_length=16)),
                ("confidence", models.FloatField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mood_history", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="UserInteraction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("interaction_type", models.CharField(choices=[("like", "Like"), ("dislike", "Dislike"), ("skip", "Skip"), ("favorite", "Favorite"), ("play", "Play"), ("complete", "Complete")], max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("song", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.song")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="interactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddField(
            model_name="playlist",
            name="songs",
            field=models.ManyToManyField(related_name="playlists", through="api.PlaylistSong", to="api.song"),
        ),
        migrations.AddConstraint(
            model_name="playlistsong",
            constraint=models.UniqueConstraint(fields=("playlist", "position"), name="unique_playlist_position"),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(fields=("user", "song"), name="unique_user_favorite"),
        ),
        migrations.AddIndex(
            model_name="song",
            index=models.Index(fields=["mood", "energy_level"], name="api_song_mood_energ_9a9a8d_idx"),
        ),
        migrations.AddIndex(
            model_name="song",
            index=models.Index(fields=["language", "genre"], name="api_song_languag_genre_1e0d93_idx"),
        ),
        migrations.AddIndex(
            model_name="listeninghistory",
            index=models.Index(fields=["user", "-played_at"], name="api_listen_user_id_4b5f53_idx"),
        ),
        migrations.AddIndex(
            model_name="userinteraction",
            index=models.Index(fields=["user", "interaction_type", "-created_at"], name="api_userint_user_id_8f6ef4_idx"),
        ),
    ]
