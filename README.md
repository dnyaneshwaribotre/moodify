# Moodify — mood-based music app

Tell Moodify how you feel (typed, spoken, emoji, English / Hindi / Marathi / Hinglish) and it builds a
playlist with **trending hits** and **famous old classics** that match your mood.

- **Frontend:** React 18 + Vite
- **Backend:** Django 5 + Django REST Framework + JWT login
- **Database:** PostgreSQL (installed normally, no containers needed)
- **AI tools** (all work offline and free, no API key needed):
  1. **Mood analyzer** – understands words, negation ("not happy"), emoji 😭, Hinglish ("aaj udaas hoon"), Hindi/Marathi script, activities ("gym", "study"), and requests like *"old Marathi songs"* or *"latest hits"*.
  2. **AI recommender** – ranks songs by mood, energy, language, your favourites/history, and gives a **reason for every song**. Results are split into *Trending now*, *Famous classics* and *More you may like*.
  3. **Voice input** – press the mic and speak your mood (Chrome / Edge / Safari).
  4. **AI insight** on the dashboard – your most frequent recent mood plus a time-of-day suggestion.
  5. **Optional Claude upgrade** – add an `ANTHROPIC_API_KEY` and Claude reads the mood instead (falls back to the built-in analyzer automatically on any error).
- **Songs:** 400+ real songs, about 70% Indian (Hindi, Marathi, Punjabi, Tamil, Telugu) plus English hits and instrumentals, from the 1950s to 2025, in `backend/api/data/songs.csv`.
- **Indian music first:** recommendations favour Indian languages by default. On the Mood studio page you can pick *All Indian / Hindi / Marathi / Punjabi / Tamil / Telugu / English / Everything*, or just write it ("old Marathi songs").
- **Click and it plays, like Spotify:** press any song and it plays inside the app, and the rest of the list plays after it. Full songs play through YouTube's embedded player when an embeddable video is found. Song links open YouTube, never Apple Music. Spotify Web API is used for optional track metadata/search; it does not supply unrestricted full-song audio.

```
moodify/
├── frontend/   React app
├── backend/    Django API, AI tools, song catalog (api/data/songs.csv)
├── database/   PostgreSQL setup script + notes
├── dataset/    keyword lists
└── docs/
```

---

## What you need installed

| Tool | Version | Check with |
|---|---|---|
| Python | 3.10 or newer | `python --version` |
| Node.js + npm | 18 or newer | `node --version` |
| PostgreSQL | 14 or newer | `psql --version` |

Install PostgreSQL if you don't have it (details in `database/README.md`):

- **Windows:** installer from https://www.postgresql.org/download/windows/ (remember the `postgres` password, keep port 5432)
- **macOS:** `brew install postgresql@16 && brew services start postgresql@16`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install -y postgresql postgresql-contrib && sudo systemctl start postgresql`

---

## Run it (step by step)

Open a terminal in the project folder (`moodify/`).

### 1. Create the database (once)

```bash
# Windows / macOS (asks for the postgres password)
psql -U postgres -f database/create_database.sql

# Ubuntu / Debian
sudo -u postgres psql -f database/create_database.sql
```

> Windows: if `psql` is not found, use `"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -f database/create_database.sql`.

This creates user `moodify` / password `moodify` and database `moodify`.

### 2. Backend setup

**Windows (PowerShell / cmd):**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

**macOS / Linux:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

(PowerShell may block `activate`; run `Set-ExecutionPolicy -Scope Process Bypass` first.)

### 3. Create tables and load the songs

```bash
python manage.py migrate
python manage.py seed_songs
```

### 4. (Optional) create an admin user

```bash
python manage.py createsuperuser
```

Admin panel: http://127.0.0.1:8000/admin/

### 5. Start the backend

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ — it should say the backend is running. Leave this terminal running.

> The backend (port 8000) only serves the API. **The app you use is the frontend at http://localhost:5173 (step 7).**

### 6. Playing songs (nothing to run)

Press play on any song. The first time, the backend searches YouTube for an embeddable full-song video and saves its ID in PostgreSQL. iTunes may still be used for cover art and metadata, but its 30-second audio previews are not played.

Optional, to get all cover art up front: `python manage.py enrich_songs` (about 10 minutes).

### 7. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**, create an account, and go to **Mood studio**.

Things to try: *"I feel nostalgic, play famous old Hindi songs"*, *"latest Marathi party songs"*,
*"need to focus and study"*, *"aaj bahut udaas hoon 😢"*, or press the 🎤 button and speak.

> If the API runs on a different address, copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL`.

---

## Full songs on YouTube

With a YouTube Data API v3 key, Moodify searches for an embeddable YouTube video and plays it in the official embedded player. Apple/iTunes 30-second previews are no longer used as a playback fallback. If a video cannot be found or embedded, use the YouTube link on the song row to open YouTube search/results.

1. Go to https://console.cloud.google.com/ and create a project (any name).
2. Open **APIs & Services → Library**, search **YouTube Data API v3**, click **Enable**.
3. Open **APIs & Services → Credentials → Create credentials → API key** and copy it.
4. Put it in `backend/.env`:
   ```
   YOUTUBE_API_KEY=your-key-here
   ```
5. Restart the backend (`python manage.py runserver`).

Notes:
- The free quota is about **100 search requests per day**. A song is looked up only the first time anyone plays it, then its video ID is saved in PostgreSQL. If quota is exhausted, new songs will open YouTube search instead of playing a 30-second preview.
- To pre-load the most popular songs in advance: `python manage.py fetch_youtube_ids --limit 90` (once a day).
- If a particular video can't be embedded, Moodify won't switch to a 30-second preview; open the YouTube link on the song row instead.

---

## Optional: Spotify Web API (track metadata/search)

Spotify's Web API can provide track names, artists, album artwork, durations, and Spotify links. It does **not** provide unrestricted full-song audio to a third-party app. Moodify therefore uses YouTube's official embedded player for full-song playback.

1. Create an app at https://developer.spotify.com/dashboard.
2. Copy the Client ID and Client Secret into `backend/.env`:
   ```
   SPOTIFY_CLIENT_ID=your-client-id
   SPOTIFY_CLIENT_SECRET=your-client-secret
   ```
3. Restart Django. Search with `GET /api/spotify/search/?q=Tum%20Hi%20Ho`.

Keep Spotify credentials only in the Django backend; never add them to a `VITE_` frontend variable.

---

## Optional: use Claude for mood analysis

Edit `backend/.env`:

```
ANTHROPIC_API_KEY=your-key-here
```

Restart the backend. The result card then shows **Claude AI** instead of **Moodify AI**. Without a key
(or if a request fails) the built-in analyzer is used, so the app always works.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `connection refused` / `could not connect to server` | PostgreSQL isn't running. Start it (Windows: Services → postgresql; macOS: `brew services start postgresql@16`; Linux: `sudo systemctl start postgresql`). |
| `password authentication failed for user "moodify"` | Step 1 wasn't run, or `backend/.env` has different DB values. |
| `psql` not found (Windows) | Add `C:\Program Files\PostgreSQL\16\bin` to PATH or use the full path. |
| `permission denied to create database` when testing | Re-run step 1 (the user needs `CREATEDB`), or `psql -U postgres -c "ALTER ROLE moodify CREATEDB;"`. |
| Frontend loads but login/API calls fail | Backend isn't running on port 8000, or `CORS_ALLOWED_ORIGINS` in `backend/.env` doesn't include your frontend URL. |
| Song does not play / "No audio found" | Check backend internet access, `YOUTUBE_API_KEY` in `backend/.env`, YouTube Data API v3 enablement, and quota. If embedding is blocked, use the YouTube link on the song row. |
| Song does not play in-app | Check `YOUTUBE_API_KEY`, YouTube Data API v3 quota, and whether the selected video permits embedding. The YouTube link opens search results if no embeddable ID is available. |
| Too much English | Pick *All Indian* (default) on the Mood studio page, or look at the Trending tabs. |
| Voice button says unsupported | Use Chrome, Edge or Safari. |
| Port 8000/5173 in use | `python manage.py runserver 8001` and set `VITE_API_BASE_URL`; or `npm run dev -- --port 5174` (and add that origin to `CORS_ALLOWED_ORIGINS`). |

---

## Handy commands

```bash
# backend (venv active, inside backend/)
python manage.py test             # backend tests (29)
python manage.py seed_songs       # (re)load catalog; safe to repeat
python manage.py seed_songs --enrich
python manage.py enrich_songs     # optional: pre-load cover art/metadata
python manage.py fetch_youtube_ids --limit 90   # optional, needs YOUTUBE_API_KEY

# frontend (inside frontend/)
npm run lint
npm run build                     # production build in frontend/dist
```

Reset the database: see `database/README.md`.

## Keeping "trending" fresh

"Trending" means recently released (2021+), ranked by popularity plus how often people play a song
inside Moodify. To add songs, append rows to `backend/api/data/songs.csv`
(`title,artist,year,language,genre,mood,emotion,energy,popularity`), then run `python manage.py seed_songs`
and `python manage.py enrich_songs`. Moods: happy, sad, calm, energetic, romantic, angry, focused, party,
sleepy, nostalgic, chill.

## API overview

| Endpoint | Purpose |
|---|---|
| `POST /api/auth/register/`, `/login/`, `/refresh/`, `/logout/` | JWT auth |
| `POST /api/ai/analyze-mood/` | mood, emotion, energy, language, era from text |
| `POST /api/ai/recommend/` | trending + classic sections with reasons (login required) |
| `GET /api/ai/insights/` | personal mood insight |
| `GET /api/songs/<id>/playback/` | YouTube video ID for embedded playback; never serves iTunes previews |
| `GET /api/spotify/search/?q=...` | optional Spotify track metadata/search |
| `GET /api/trending/?category=trending\|classics\|hindi\|marathi\|punjabi\|south\|global` | browse songs (trending/classics are Indian) |
| `/api/playlists/`, `/favorites/`, `/history/`, `/mood-history/`, `/interactions/` | user data |

## Notes

- Song data is metadata only (title, artist, year). Audio is never stored: iTunes may supply artwork/metadata, Spotify may supply track metadata, and full-song playback uses YouTube's official embedded player, under their terms.
- For production: set a strong `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, real `DJANGO_ALLOWED_HOSTS`, and a non-default database password.
