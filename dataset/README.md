# Dataset

- The song catalog used by the app is `backend/api/data/songs.csv` (loaded by `python manage.py seed_songs`).
- `songs_template.csv` – empty schema template.
- `mood_keywords.csv`, `energy_keywords.csv` – reference keyword lists from the original analyzer; the live lexicon is in `backend/api/mood_analyzer.py`.
