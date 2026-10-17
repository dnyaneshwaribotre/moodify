import time

from django.core.management.base import BaseCommand

from api.models import Song
from api.youtube import find_video_id, youtube_enabled


class Command(BaseCommand):
    help = (
        "Pre-fetch YouTube video ids for the most popular songs so they play instantly. Needs YOUTUBE_API_KEY. "
        "The free YouTube quota allows about 100 searches a day, so run it with --limit 90 once a day."
    )

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=90)

    def handle(self, *args, **options):
        if not youtube_enabled():
            self.stderr.write(self.style.ERROR("Set YOUTUBE_API_KEY in backend/.env first (see README)."))
            return
        songs = Song.objects.filter(youtube_id="").order_by("-popularity_score")[: options["limit"]]
        done = 0
        for song in songs:
            video_id = find_video_id(song)
            if video_id is None:
                self.stderr.write("YouTube refused or failed (quota used up?). Run again tomorrow.")
                break
            if video_id:
                song.youtube_id = video_id
                song.save(update_fields=["youtube_id"])
                done += 1
            time.sleep(0.2)
        self.stdout.write(self.style.SUCCESS(f"Saved YouTube ids for {done} songs."))
