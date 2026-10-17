import time
import urllib.error

from django.core.management.base import BaseCommand

from api.itunes import apply_match, fetch_itunes, pick_best_match
from api.models import Song

class Command(BaseCommand):
    help = (
        "Fetch 30-second preview audio, cover art and duration for songs from the free iTunes "
        "Search API (no API key). Run it once after seed_songs; needs internet access."
    )

    def add_arguments(self, parser):
        parser.add_argument("--country", default="US", help="iTunes store country code (default US).")
        parser.add_argument("--delay", type=float, default=1.2, help="Seconds between requests (default 1.2).")
        parser.add_argument("--all", action="store_true", help="Refresh songs that already have a preview.")
        parser.add_argument("--limit", type=int, default=0, help="Only process this many songs.")

    def handle(self, *args, **options):
        songs = Song.objects.all() if options["all"] else Song.objects.filter(preview_url="")
        if options["limit"]:
            songs = songs[: options["limit"]]
        songs = list(songs)
        found = missing = failed = 0
        for index, song in enumerate(songs, start=1):
            try:
                results = fetch_itunes(f"{song.title} {song.artist}", options["country"])
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                failed += 1
                self.stderr.write(f"[{index}/{len(songs)}] network problem for '{song.title}': {exc}")
                if failed >= 5 and not found:
                    self.stderr.write(self.style.ERROR(
                        "Several requests failed in a row - check your internet connection and retry."))
                    return
                time.sleep(max(options["delay"], 5))
                continue
            match = pick_best_match(song, results)
            if match:
                apply_match(song, match)
                song.save()
                found += 1
            else:
                missing += 1
            if index % 20 == 0:
                self.stdout.write(f"  {index}/{len(songs)} processed ({found} with previews)")
            time.sleep(options["delay"])
        self.stdout.write(self.style.SUCCESS(
            f"Done. {found} songs now have previews, {missing} had no match, {failed} requests failed."))
