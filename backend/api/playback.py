"""Resolve permitted playback through YouTube; iTunes is only used for artwork/metadata."""
from django.core.cache import cache
from django.utils.http import urlencode

from .itunes import apply_match, fetch_itunes, pick_best_match
from .audius import find_stream_url
from .saavn import find_saavn_track
from .youtube import find_video_id


def youtube_search_url(song):
    query = f"{song.title} {song.artist} official audio"
    return "https://www.youtube.com/results?" + urlencode({"search_query": query})


def _resolve_youtube_playback(song):
    changed = False
    if not song.youtube_id and not cache.get(f"no-youtube:{song.pk}"):
        video_id = find_video_id(song)
        if video_id:
            song.youtube_id = video_id
            changed = True
        elif video_id == "":
            cache.set(f"no-youtube:{song.pk}", True, 60 * 60 * 24)

    # Backup full-song source (Audius, no key). Cached so we only look it up once per song.
    audius_key = f"audius:{song.pk}"
    audius_url = cache.get(audius_key)
    if audius_url is None:
        audius_url = find_stream_url(song)
        if audius_url is not None:
            cache.set(audius_key, audius_url, 60 * 60 * 24)
    audius_url = audius_url or ""

    # Fetch artwork/metadata, and a 30-second preview used only as a fallback when no YouTube video plays.
    if not song.image_url or not song.album or not song.preview_url:
        try:
            matches = fetch_itunes(f"{song.title} {song.artist}", "US")
            match = pick_best_match(song, matches)
        except Exception:  # noqa: BLE001 - offline/rate limited; metadata is optional
            match = None
        if match:
            old_external_url = song.external_url
            apply_match(song, match)
            # Apple Music is not the playback destination.
            song.external_url = youtube_search_url(song)
            changed = True
        elif song.external_url.startswith("https://music.apple.com/"):
            song.external_url = youtube_search_url(song)
            changed = True

    # Keep every song's outbound link pointed at YouTube, including when the API key
    # is absent or no embeddable video was found.
    desired_url = (
        f"https://www.youtube.com/watch?v={song.youtube_id}"
        if song.youtube_id else youtube_search_url(song)
    )
    if song.external_url != desired_url:
        song.external_url = desired_url
        changed = True
    if changed:
        song.save()

    # Prefer the full Audius song over the 30-second iTunes clip as the backup.
    fallback_url = audius_url or song.preview_url
    source = "youtube" if song.youtube_id else ("preview" if fallback_url else "none")
    return {
        "id": song.pk,
        "source": source,
        "youtube_id": song.youtube_id,
        "preview_url": fallback_url,  # fallback if the YouTube video can't be embedded
        "image_url": song.image_url,
        "duration": song.duration,
        "external_url": desired_url,
        "youtube_search_url": youtube_search_url(song),
    }


def resolve_playback(song):
    """JioSaavn first (full song, plain audio). If it has no match or is unreachable, use the YouTube/Audius flow."""
    saavn_key = f"saavn:{song.pk}"
    track = cache.get(saavn_key)
    if track is None:
        track = find_saavn_track(song)
        if track is not None:  # don't cache "unreachable"
            cache.set(saavn_key, track, 60 * 60 * 6)
    if track and track.get("url"):
        return {
            "id": song.pk,
            "source": "preview",  # the app's plain <audio> player
            "youtube_id": "",
            "preview_url": track["url"],
            "image_url": song.image_url or track.get("image_url", ""),
            "duration": song.duration,
            "external_url": song.external_url,
            "youtube_search_url": youtube_search_url(song),
        }
    return _resolve_youtube_playback(song)
