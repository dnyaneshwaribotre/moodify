"""Find the YouTube video for a song with the official YouTube Data API (needs a free API key)."""
import json
import re
import urllib.error
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache

log = logging.getLogger(__name__)
QUOTA_FLAG = "youtube-quota-exhausted"


def youtube_enabled():
    return bool(settings.YOUTUBE_API_KEY) and not cache.get(QUOTA_FLAG)


def scrape_video_id(song):
    """No-key fallback: read the first video id from YouTube's public search page. '' if none, None on failure."""
    query = urllib.parse.urlencode({"search_query": f"{song.title} {song.artist} official audio", "sp": "EgIQAQ%3D%3D"})
    request = urllib.request.Request(
        f"https://www.youtube.com/results?{query}",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
                 "Accept-Language": "en-US,en;q=0.9"},
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            html = response.read().decode("utf-8", "ignore")
    except Exception as exc:  # noqa: BLE001
        log.warning("YouTube search-page lookup failed: %s", exc)
        return None
    match = re.search(r'"videoId":"([A-Za-z0-9_-]{11})"', html)
    return match.group(1) if match else ""


def find_video_id(song):
    """Return an embeddable video id, '' if none found, or None if lookup could not be done right now."""
    if not youtube_enabled():
        return scrape_video_id(song)
    params = urllib.parse.urlencode({
        "part": "snippet", "type": "video", "videoEmbeddable": "true", "videoSyndicated": "true",
        "videoCategoryId": "10", "maxResults": 3, "key": settings.YOUTUBE_API_KEY,
        "q": f"{song.title} {song.artist} official audio",
    })
    try:
        with urllib.request.urlopen(f"https://www.googleapis.com/youtube/v3/search?{params}", timeout=8) as response:
            items = json.loads(response.read().decode("utf-8")).get("items", [])
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 429):  # daily quota used up (or key restricted): stop trying for a while
            cache.set(QUOTA_FLAG, True, 60 * 60)
            log.warning("YouTube API refused the request (HTTP %s): quota used up or key not allowed.", exc.code)
        return scrape_video_id(song)
    except Exception as exc:  # noqa: BLE001
        log.warning("YouTube lookup failed: %s", exc)
        return None
    for item in items:
        video_id = item.get("id", {}).get("videoId")
        if video_id:
            return video_id
    return ""
