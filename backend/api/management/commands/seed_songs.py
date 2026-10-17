import csv
from pathlib import Path
from urllib.parse import quote_plus

from django.core.management import call_command
from django.core.management.base import BaseCommand

from api.models import Song

CATALOG = Path(__file__).resolve().parents[2] / "data" / "songs.csv"


class Command(BaseCommand):
    help = (
        "Load the Moodify song catalog (trending hits + famous old songs) into PostgreSQL. "
        "Safe to run repeatedly. Use --enrich to also fetch 30-second previews and cover art."
    )

    def add_arguments(self, parser):
        parser.add_argument("--enrich", action="store_true",
                            help="After seeding, fetch previews/artwork from the iTunes Search API (needs internet).")

    def handle(self, *args, **options):
        # Remove the placeholder tracks that older versions of this project inserted.
        removed, _ = Song.objects.filter(provider="demo").delete()
        created = updated = 0
        with open(CATALOG, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                query = quote_plus(f"{row['title']} {row['artist']}")
                defaults = {
                    "provider": "catalog",
                    "genre": row["genre"],
                    "language": row["language"],
                    "mood": row["mood"],
                    "emotion": row["emotion"],
                    "energy_level": row["energy"],
                    "popularity_score": int(row["popularity"]),
                    "release_year": int(row["year"]),
                }
                song, was_created = Song.objects.get_or_create(
                    title=row["title"], artist=row["artist"],
                    defaults={**defaults, "external_url": f"https://www.youtube.com/results?search_query={query}"},
                )
                if was_created:
                    created += 1
                else:
                    for key, value in defaults.items():
                        setattr(song, key, value)
                    song.save()
                    updated += 1
        self.stdout.write(self.style.SUCCESS(
            f"Catalog ready: {created} added, {updated} refreshed, {removed} placeholder rows removed."
        ))
        if options["enrich"]:
            call_command("enrich_songs")
