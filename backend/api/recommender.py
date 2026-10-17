"""Builds the mood session shown to the user: trending hits + famous classics + more you'll like."""
from __future__ import annotations

from django.db.models import Q

from .models import Favorite, ListeningHistory, Song, UserInteraction
from .recommendation_engine import MOOD_COMPAT, pick_diverse, rank_recommendations
from .serializers import SongSerializer

SECTION_META = {
    "trending": ("Trending now", "Recent hits that fit this mood"),
    "classic": ("Famous classics", "Old favourites that still hit the spot"),
    "popular": ("More you may like", "Evergreen popular picks"),
}


def build_session(user, mood, energy_level="medium", language=None, era_preference=None, per_section=8):
    moods = MOOD_COMPAT.get(mood, [mood, "chill"])
    mood_filter = Q(mood__in=set(moods) | {mood})
    if language and language not in ("indian", "any"):
        mood_filter |= Q(language=language)  # always include the requested language, ranked by mood fit
    songs = Song.objects.filter(mood_filter)
    candidates = [dict(item) for item in SongSerializer(songs, many=True).data]
    if len(candidates) < 12:  # tiny catalog fallback
        candidates = [dict(item) for item in SongSerializer(Song.objects.all()[:200], many=True).data]

    profile, favorites, history, interactions = {}, [], [], []
    if user and user.is_authenticated:
        profile_obj = getattr(user, "profile", None)
        if profile_obj:
            profile = {
                "preferred_genres": profile_obj.preferred_genres,
                "preferred_languages": profile_obj.preferred_languages,
                "favorite_artists": profile_obj.favorite_artists,
                "preferred_mood": profile_obj.preferred_mood,
            }
        favorites = list(Favorite.objects.filter(user=user).values("song_id"))
        history = list(ListeningHistory.objects.filter(user=user).values("song_id")[:50])
        interactions = list(UserInteraction.objects.filter(user=user).values("song_id", "interaction_type")[:200])

    ranked = rank_recommendations(candidates, mood, energy_level, profile, favorites, history, interactions,
                                  language=language)
    order = ["trending", "classic", "popular"]
    if era_preference in ("classic", "trending"):
        order.remove(era_preference)
        order.insert(0, era_preference)

    sections = []
    for position, key in enumerate(order):
        pool = [s for s in ranked if s.get("era") == key]
        size = per_section + 4 if position == 0 and era_preference else per_section
        if key == "popular":
            size = min(size, 6)
        chosen = pick_diverse(pool, size)
        if chosen:
            title, subtitle = SECTION_META[key]
            sections.append({"key": key, "title": title, "subtitle": subtitle, "songs": chosen})
    return sections
