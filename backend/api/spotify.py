"""Spotify Web API helpers for track metadata/search (not audio streaming)."""
import base64
import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache

log = logging.getLogger(__name__)
TOKEN_CACHE_KEY = "spotify-client-credentials-token"


def spotify_enabled():
    return bool(settings.SPOTIFY_CLIENT_ID and settings.SPOTIFY_CLIENT_SECRET)


def _access_token():
    cached = cache.get(TOKEN_CACHE_KEY)
    if cached:
        return cached
    credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
    auth = base64.b64encode(credentials).decode("ascii")
    request = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(),
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))
    token = payload["access_token"]
    cache.set(TOKEN_CACHE_KEY, token, max(60, int(payload.get("expires_in", 3600)) - 60))
    return token


def search_tracks(query, limit=10):
    """Return Spotify track metadata and Spotify URLs. No audio files are returned."""
    if not spotify_enabled():
        return None
    params = urllib.parse.urlencode({"q": query, "type": "track", "limit": max(1, min(limit, 20))})
    request = urllib.request.Request(
        f"https://api.spotify.com/v1/search?{params}",
        headers={"Authorization": f"Bearer {_access_token()}"},
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))
    tracks = payload.get("tracks", {}).get("items", [])
    return [{
        "id": track.get("id"),
        "title": track.get("name"),
        "artist": ", ".join(a.get("name", "") for a in track.get("artists", [])),
        "album": (track.get("album") or {}).get("name", ""),
        "duration_ms": track.get("duration_ms"),
        "spotify_url": (track.get("external_urls") or {}).get("spotify", ""),
        "image_url": next(iter((track.get("album") or {}).get("images", [])), {}).get("url", ""),
        "preview_url": track.get("preview_url") or "",
    } for track in tracks]
