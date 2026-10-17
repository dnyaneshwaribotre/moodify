"""iTunes Search API helpers (free, no key): 30-second previews, cover art and duration."""
import json
import re
import urllib.parse
import urllib.request

ITUNES_URL = "https://itunes.apple.com/search"


def _norm(value):
    return re.sub(r"[^a-z0-9 ]+", " ", (value or "").lower()).split()


def pick_best_match(song, results):
    """Choose the iTunes result whose title and artist best match our song."""
    title_tokens = set(_norm(song.title))
    artist_tokens = set(_norm(song.artist)) - {"and", "feat", "ft"}
    best, best_score = None, 0.0
    for item in results:
        if not item.get("previewUrl"):
            continue
        item_title = set(_norm(item.get("trackName")))
        item_artist = set(_norm(item.get("artistName")))
        if not title_tokens or not item_title:
            continue
        title_score = len(title_tokens & item_title) / len(title_tokens | item_title)
        artist_score = len(artist_tokens & item_artist) / max(len(artist_tokens), 1)
        score = title_score * 0.7 + artist_score * 0.3
        if title_score >= 0.5 and score > best_score:
            best, best_score = item, score
    return best


def fetch_itunes(term, country):
    params = urllib.parse.urlencode({
        "term": term, "media": "music", "entity": "song", "limit": 8, "country": country,
    })
    request = urllib.request.Request(f"{ITUNES_URL}?{params}", headers={"User-Agent": "Moodify/1.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8")).get("results", [])


def apply_match(song, match):
    song.preview_url = match["previewUrl"]
    song.image_url = (match.get("artworkUrl100") or "").replace("100x100", "400x400")
    song.album = (match.get("collectionName") or "")[:255]
    song.provider_track_id = str(match.get("trackId", ""))
    if match.get("trackTimeMillis"):
        song.duration = round(match["trackTimeMillis"] / 1000)
    # iTunes is used for artwork/metadata only; outbound playback links belong to YouTube.
    song.provider = "itunes"
