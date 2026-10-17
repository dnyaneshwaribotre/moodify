"""Audius (free, no API key): full-length track streaming, used as a backup when YouTube can't play a song."""
import json
import logging
import urllib.parse
import urllib.request

from .itunes import _norm

log = logging.getLogger(__name__)
API = "https://api.audius.co/v1"
APP_NAME = "moodify"


def find_stream_url(song):
    """Return a full-song stream URL from Audius, '' if no good match, None if Audius couldn't be reached."""
    params = urllib.parse.urlencode({"query": f"{song.title} {song.artist}", "limit": 10, "app_name": APP_NAME})
    request = urllib.request.Request(f"{API}/tracks/search?{params}", headers={"User-Agent": "Moodify/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            tracks = json.loads(response.read().decode("utf-8")).get("data", [])
    except Exception as exc:  # noqa: BLE001
        log.warning("Audius lookup failed: %s", exc)
        return None
    title_tokens = set(_norm(song.title))
    artist_tokens = set(_norm(song.artist)) - {"and", "feat", "ft"}
    best, best_score = None, 0.0
    for track in tracks:
        if track.get("is_streamable") is False or not track.get("id"):
            continue
        t_tokens = set(_norm(track.get("title")))
        a_tokens = set(_norm((track.get("user") or {}).get("name")))
        if not title_tokens or not t_tokens:
            continue
        title_score = len(title_tokens & t_tokens) / len(title_tokens | t_tokens)
        artist_score = len(artist_tokens & (a_tokens | t_tokens)) / max(len(artist_tokens), 1)
        score = title_score * 0.7 + artist_score * 0.3
        if title_score >= 0.6 and score > best_score:
            best, best_score = track, score
    if not best:
        return ""
    return f"{API}/tracks/{best['id']}/stream?app_name={APP_NAME}"
