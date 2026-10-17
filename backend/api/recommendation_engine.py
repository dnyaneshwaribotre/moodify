from __future__ import annotations

from collections import defaultdict
from typing import Any

DEFAULT_WEIGHTS = {
    "mood": 0.30, "energy": 0.15, "genre": 0.15, "language": 0.10,
    "preferences": 0.10, "history": 0.10, "trending": 0.10,
}

# For each target mood: which other song moods still fit.
MOOD_COMPAT = {
    "calm": ["calm", "sleepy", "chill", "focused"],
    "happy": ["happy", "energetic", "party", "chill"],
    "sad": ["sad", "nostalgic", "chill", "calm"],
    "energetic": ["energetic", "party", "happy", "angry"],
    "romantic": ["romantic", "chill", "nostalgic"],
    "angry": ["angry", "energetic", "party"],
    "focused": ["focused", "calm", "chill"],
    "party": ["party", "energetic", "happy"],
    "sleepy": ["sleepy", "calm", "chill"],
    "nostalgic": ["nostalgic", "sad", "romantic", "chill"],
    "chill": ["chill", "calm", "happy", "focused"],
}
INDIAN_LANGUAGES = {"hindi", "marathi", "punjabi", "tamil", "telugu"}
ENERGY_COMPAT = {"low": ["medium"], "medium": ["low", "high"], "high": ["medium"]}


def _mood_compatible(song_mood, target):
    return song_mood in MOOD_COMPAT.get(target, []) and song_mood != target


def _energy_compatible(song_energy, target):
    return song_energy in ENERGY_COMPAT.get(target, [])


def rank_recommendations(candidates, mood, energy_level, profile=None, favorites=None, history=None,
                         interactions=None, language=None):
    """Score songs for a mood. Every result carries `recommendation_score` and human-readable `reasons`."""
    profile = profile or {}
    favorites = favorites or []
    history = history or []
    interactions = interactions or []
    fav = {x.get("song_id") or x.get("id") for x in favorites}
    hist = {x.get("song_id") or x.get("id") for x in history}
    liked = {x.get("song_id") for x in interactions if x.get("interaction_type") == "like"}
    skipped = {x.get("song_id") for x in interactions if x.get("interaction_type") == "skip"}
    preferred_genres = profile.get("preferred_genres", [])
    preferred_languages = profile.get("preferred_languages", [])
    artists = [a.lower() for a in profile.get("favorite_artists", []) if a]
    preferred_mood = profile.get("preferred_mood")
    # language: None/"indian" (default) favours all Indian languages, a specific language favours just that one,
    # "any" turns the language preference off.
    language = (language or "indian").lower()
    wanted_language = language if language not in ("indian", "any") else None

    scored = []
    for song in candidates:
        score = 0.0
        reasons = []
        if song.get("mood") == mood:
            score += DEFAULT_WEIGHTS["mood"]
            reasons.append(f"Matches your {mood} mood")
        elif _mood_compatible(song.get("mood"), mood):
            score += DEFAULT_WEIGHTS["mood"] * 0.5
            reasons.append(f"Close to your {mood} mood")
        if song.get("energy_level") == energy_level:
            score += DEFAULT_WEIGHTS["energy"]
            reasons.append(f"{energy_level.capitalize()} energy, like you asked")
        elif _energy_compatible(song.get("energy_level"), energy_level):
            score += DEFAULT_WEIGHTS["energy"] * 0.4
        if wanted_language and song.get("language") == wanted_language:
            score += 0.6  # the person asked for this language explicitly
            reasons.insert(0, f"{wanted_language.capitalize()} song, as you asked")
        elif language == "indian" and song.get("language") in INDIAN_LANGUAGES:
            score += 0.3
        elif preferred_languages and song.get("language") in preferred_languages:
            score += DEFAULT_WEIGHTS["language"]
            reasons.append("In a language you like")
        if song.get("genre") in preferred_genres:
            score += DEFAULT_WEIGHTS["genre"]
            reasons.append(f"You like {song.get('genre')}")
        if any(a in song.get("artist", "").lower() for a in artists):
            score += DEFAULT_WEIGHTS["preferences"] * 0.5
            reasons.append("From an artist you follow")
        if preferred_mood and song.get("mood") == preferred_mood:
            score += DEFAULT_WEIGHTS["preferences"] * 0.3
        if song.get("id") in fav:
            score += DEFAULT_WEIGHTS["history"] * 0.4
            reasons.append("One of your favourites")
        if song.get("id") in liked:
            score += DEFAULT_WEIGHTS["history"] * 0.5
        if song.get("id") in skipped:
            score -= DEFAULT_WEIGHTS["history"] * 0.3
        if song.get("id") in hist:
            score += DEFAULT_WEIGHTS["history"] * 0.2
        score += (song.get("popularity_score") or 0) / 100 * DEFAULT_WEIGHTS["trending"]
        era = song.get("era")
        if era == "trending" and (song.get("popularity_score") or 0) >= 85:
            reasons.append("Trending right now")
        elif era == "classic" and song.get("release_year"):
            reasons.append(f"Timeless classic ({song['release_year']})")
        scored.append({**song, "recommendation_score": round(score, 3), "reasons": reasons[:3]})
    return sorted(scored, key=lambda x: x["recommendation_score"], reverse=True)


def pick_diverse(ranked, count, per_artist=2):
    """Take the top `count` songs without letting one artist dominate."""
    taken, seen = [], defaultdict(int)
    for song in ranked:
        artist = song.get("artist", "").split("&")[0].strip().lower()
        if seen[artist] >= per_artist:
            continue
        seen[artist] += 1
        taken.append(song)
        if len(taken) >= count:
            break
    return taken
