"""JioSaavn (unofficial, free, no key): full-length song streams, tried first for playback.

Uses a community JioSaavn API (https://github.com/sumitkolhe/jiosaavn-api). Public hosts can be slow or go
offline, so the host is configurable with SAAVN_API_URL in backend/.env (you can self-host it)."""
import json
import logging
import os
import urllib.parse
import urllib.request

from .itunes import _norm

log = logging.getLogger(__name__)
DEFAULT_API = "https://saavn.dev"


def saavn_base():
    return (os.getenv("SAAVN_API_URL", "").strip() or DEFAULT_API).rstrip("/")


def find_saavn_track(song):
    """Return {'url', 'image_url'} for the best JioSaavn match, {} if none, None if the API couldn't be reached."""
    params = urllib.parse.urlencode({"query": f"{song.title} {song.artist}", "limit": 10})
    request = urllib.request.Request(
        f"{saavn_base()}/api/search/songs?{params}",
        headers={"User-Agent": "Mozilla/5.0 Moodify/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        log.warning("JioSaavn lookup failed: %s", exc)
        return None
    data = payload.get("data") or {}
    results = data.get("results", []) if isinstance(data, dict) else data
    title_tokens = set(_norm(song.title))
    artist_tokens = set(_norm(song.artist)) - {"and", "feat", "ft"}
    best, best_score = None, 0.0
    for item in results or []:
        links = item.get("downloadUrl") or []
        if not links or not title_tokens:
            continue
        item_title = set(_norm(item.get("name")))
        artists = item.get("artists") or {}
        names = " ".join(a.get("name", "") for a in (artists.get("primary") or artists.get("all") or []))
        item_artist = set(_norm(names or item.get("primaryArtists") or ""))
        if not item_title:
            continue
        title_score = len(title_tokens & item_title) / len(title_tokens | item_title)
        artist_score = len(artist_tokens & item_artist) / max(len(artist_tokens), 1)
        score = title_score * 0.7 + artist_score * 0.3
        if title_score >= 0.5 and score > best_score:
            best, best_score = item, score
    if not best:
        return {}
    link = best["downloadUrl"][-1]  # last entry is the highest quality
    url = link.get("url") or link.get("link") or ""
    images = best.get("image") or []
    image = (images[-1].get("url") or images[-1].get("link") or "") if images else ""
    return {"url": url, "image_url": image} if url else {}
