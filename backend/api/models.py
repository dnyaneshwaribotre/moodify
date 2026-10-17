from django.conf import settings
from django.db import models


TRENDING_FROM_YEAR = 2021
CLASSIC_UNTIL_YEAR = 2010


def era_for_year(year):
    if not year:
        return "popular"
    if year >= TRENDING_FROM_YEAR:
        return "trending"
    if year <= CLASSIC_UNTIL_YEAR:
        return "classic"
    return "popular"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    preferred_genres = models.JSONField(default=list, blank=True)
    preferred_languages = models.JSONField(default=list, blank=True)
    favorite_artists = models.JSONField(default=list, blank=True)
    preferred_mood = models.CharField(max_length=32, default="chill")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return f"Profile: {self.user.username}"


class Song(models.Model):
    provider = models.CharField(max_length=32, default="demo")
    provider_track_id = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True)
    genre = models.CharField(max_length=80, default="pop", db_index=True)
    language = models.CharField(max_length=40, default="english", db_index=True)
    mood = models.CharField(max_length=40, default="chill", db_index=True)
    emotion = models.CharField(max_length=40, default="neutral")
    energy_level = models.CharField(max_length=16, default="medium", db_index=True)
    duration = models.PositiveIntegerField(default=180)
    image_url = models.URLField(blank=True)
    external_url = models.URLField(blank=True)
    preview_url = models.URLField(blank=True)
    youtube_id = models.CharField(max_length=20, blank=True)
    popularity_score = models.PositiveSmallIntegerField(default=50, db_index=True)
    release_date = models.DateField(null=True, blank=True)
    release_year = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    plays = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-popularity_score", "title"]
        indexes = [
            models.Index(fields=["mood", "energy_level"]),
            models.Index(fields=["language", "genre"]),
        ]

    @property
    def era(self):
        """'trending' (recent), 'classic' (old and famous) or 'popular' (in between)."""
        return era_for_year(self.release_year)

    def __str__(self):
        return f"{self.title} — {self.artist}"


class Playlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="playlists"
    )
    name = models.CharField(max_length=180)
    mood = models.CharField(max_length=40, default="chill")
    emotion = models.CharField(max_length=40, default="neutral")
    energy_level = models.CharField(max_length=16, default="medium")
    description = models.TextField(blank=True)
    confidence = models.FloatField(default=0)
    cover_gradient = models.CharField(
        max_length=255,
        default="linear-gradient(135deg, #1f2937, #374151)",
    )
    songs = models.ManyToManyField("Song", through="PlaylistSong", related_name="playlists")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def song_count(self):
        return self.playlist_songs.count()

    @property
    def total_duration(self):
        return sum(row.song.duration for row in self.playlist_songs.select_related("song"))

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class PlaylistSong(models.Model):
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, related_name="playlist_songs"
    )
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["playlist", "position"],
                name="unique_playlist_position",
            ),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    song = models.ForeignKey(
        Song, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "song"], name="unique_user_favorite"
            ),
        ]


class ListeningHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listening_history",
    )
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)
    duration_played = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-played_at"]
        indexes = [models.Index(fields=["user", "-played_at"])]


class MoodHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mood_history"
    )
    input_text = models.TextField()
    detected_emotion = models.CharField(max_length=40)
    detected_mood = models.CharField(max_length=40)
    energy_level = models.CharField(max_length=16, default="medium")
    confidence = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class UserInteraction(models.Model):
    TYPES = [
        ("like", "Like"),
        ("dislike", "Dislike"),
        ("skip", "Skip"),
        ("favorite", "Favorite"),
        ("play", "Play"),
        ("complete", "Complete"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interactions",
    )
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "interaction_type", "-created_at"])]
