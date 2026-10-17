from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .itunes import pick_best_match
from .mood_analyzer import analyze_mood
from .models import Profile, Song

User = get_user_model()


class MoodAnalyzerTests(TestCase):
    def test_calm_request(self):
        result = analyze_mood("I had a stressful day and need peaceful relaxing music.")
        self.assertEqual(result["mood"], "calm")
        self.assertEqual(result["energy_level"], "low")

    def test_negation_is_respected(self):
        self.assertNotEqual(analyze_mood("I am not happy at all")["mood"], "happy")
        self.assertEqual(analyze_mood("I am so happy today!")["mood"], "happy")

    def test_word_boundaries(self):
        # "made" must not trigger the anger keyword "mad"
        self.assertNotEqual(analyze_mood("I made some tea")["mood"], "angry")

    def test_activity_context(self):
        self.assertEqual(analyze_mood("need songs for the gym workout")["mood"], "energetic")
        self.assertEqual(analyze_mood("I want to study and concentrate")["mood"], "focused")

    def test_emoji(self):
        self.assertEqual(analyze_mood("😭💔")["mood"], "sad")

    def test_hinglish_and_script(self):
        self.assertEqual(analyze_mood("aaj bahut udaas hoon")["mood"], "sad")
        result = analyze_mood("मैं बहुत खुश हूँ")
        self.assertEqual(result["mood"], "happy")
        self.assertEqual(result["language"], "hindi")
        self.assertEqual(analyze_mood("मला खूप आनंद आहे")["language"], "marathi")

    def test_era_and_language_requests(self):
        result = analyze_mood("play some old Marathi songs")
        self.assertEqual(result["era_preference"], "classic")
        self.assertEqual(result["requested_language"], "marathi")
        self.assertEqual(analyze_mood("latest trending hits for a party")["era_preference"], "trending")

    def test_empty_text(self):
        self.assertEqual(analyze_mood("   ")["mood"], "chill")


class ApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_songs", verbosity=0)

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tester", email="tester@example.com", password="test-pass-123")
        Profile.objects.create(user=self.user)

    def login(self):
        response = self.client.post("/api/auth/login/", {"email": "tester@example.com", "password": "test-pass-123"},
                                    format="json")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])

    def test_health(self):
        self.assertEqual(self.client.get("/api/health/").status_code, 200)

    def test_seed_is_idempotent_and_has_both_eras(self):
        count = Song.objects.count()
        call_command("seed_songs", verbosity=0)
        self.assertEqual(Song.objects.count(), count)
        self.assertGreater(Song.objects.filter(release_year__gte=2021).count(), 30)
        self.assertGreater(Song.objects.filter(release_year__lte=2010).count(), 30)

    def test_register_and_jwt_profile(self):
        response = self.client.post("/api/auth/register/",
                                    {"email": "new@example.com", "username": "newuser", "password": "test-pass-123"},
                                    format="json")
        self.assertEqual(response.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
        self.assertEqual(self.client.get("/api/auth/profile/").status_code, 200)

    def test_analyze_endpoint_public(self):
        response = self.client.post("/api/ai/analyze-mood/", {"text": "feeling romantic tonight"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["mood"], "romantic")
        self.assertEqual(response.data["engine"], "local")
        self.assertEqual(self.client.post("/api/ai/analyze-mood/", {"text": ""}, format="json").status_code, 400)

    def test_recommend_requires_login(self):
        response = self.client.post("/api/ai/recommend/", {"mood": "calm"}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_recommend_returns_trending_and_classics_with_reasons(self):
        self.login()
        response = self.client.post("/api/ai/recommend/", {"mood": "romantic", "energy_level": "low"}, format="json")
        self.assertEqual(response.status_code, 200)
        sections = {s["key"]: s["songs"] for s in response.data["sections"]}
        self.assertIn("trending", sections)
        self.assertIn("classic", sections)
        self.assertTrue(all(song["era"] == "trending" for song in sections["trending"]))
        self.assertTrue(all(song["era"] == "classic" for song in sections["classic"]))
        self.assertTrue(sections["classic"][0]["reasons"])

    def test_recommend_from_text_honours_old_marathi_request(self):
        self.login()
        response = self.client.post("/api/ai/recommend/", {"text": "old marathi songs please"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["sections"][0]["key"], "classic")
        top = [song for section in response.data["sections"] for song in section["songs"]][:3]
        self.assertTrue(any(song["language"] == "marathi" for song in top) or response.data["language"] == "marathi")

    def test_recommendations_are_indian_first_by_default(self):
        self.login()
        indian = {"hindi", "marathi", "punjabi", "tamil", "telugu"}
        for mood in ["happy", "sad", "calm", "romantic", "party", "energetic", "nostalgic"]:
            songs = [x for sec in self.client.post("/api/ai/recommend/", {"mood": mood}, format="json").data["sections"]
                     for x in sec["songs"]]
            share = sum(x["language"] in indian for x in songs) / len(songs)
            self.assertGreaterEqual(share, 0.75, f"{mood}: only {share:.0%} Indian")

    def test_language_choice_english_and_any(self):
        self.login()
        songs = [x for sec in self.client.post("/api/ai/recommend/", {"mood": "happy", "language": "english"},
                                               format="json").data["sections"] for x in sec["songs"]]
        self.assertGreaterEqual(sum(x["language"] == "english" for x in songs) / len(songs), 0.6)
        self.assertEqual(self.client.post("/api/ai/recommend/", {"mood": "happy", "language": "any"},
                                          format="json").status_code, 200)

    def test_every_mood_has_recommendations(self):
        self.login()
        for mood in ["happy", "sad", "calm", "energetic", "romantic", "angry", "focused", "party", "sleepy",
                     "nostalgic", "chill"]:
            response = self.client.post("/api/ai/recommend/", {"mood": mood}, format="json")
            self.assertGreaterEqual(response.data["total"], 6, mood)

    def test_trending_categories(self):
        indian = {"hindi", "marathi", "punjabi", "tamil", "telugu"}
        recent = self.client.get("/api/trending/?category=trending&limit=50").data
        self.assertTrue(recent and all(s["release_year"] >= 2021 and s["language"] in indian for s in recent))
        old = self.client.get("/api/trending/?category=classics&limit=50").data
        self.assertTrue(old and all(s["release_year"] <= 2010 and s["language"] in indian for s in old))
        western = self.client.get("/api/trending/?category=global&limit=50").data
        self.assertTrue(western and all(s["language"] == "english" for s in western))
        marathi = self.client.get("/api/trending/?category=marathi").data
        self.assertTrue(marathi and all(s["language"] == "marathi" for s in marathi))

    def test_play_interaction_counts_plays_and_insights(self):
        self.login()
        song = Song.objects.first()
        self.client.post("/api/interactions/", {"song_id": song.id, "interaction_type": "play"}, format="json")
        song.refresh_from_db()
        self.assertEqual(song.plays, 1)
        self.client.post("/api/mood-history/", {"input_text": "x", "detected_emotion": "joy", "detected_mood": "happy",
                                                "energy_level": "high", "confidence": 0.8}, format="json")
        insights = self.client.get("/api/ai/insights/")
        self.assertEqual(insights.status_code, 200)
        self.assertEqual(insights.data["top_mood"], "happy")


class LlmFallbackTests(TestCase):
    @override_settings(ANTHROPIC_API_KEY="")
    def test_no_key_uses_local(self):
        from .ai_service import analyze
        self.assertEqual(analyze("I feel calm")["engine"], "local")

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_network_failure_falls_back(self):
        from .ai_service import analyze
        with mock.patch("urllib.request.urlopen", side_effect=OSError("offline")):
            self.assertEqual(analyze("I feel calm")["engine"], "local")

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_valid_llm_reply_is_used_and_validated(self):
        import json
        from .ai_service import analyze
        reply = {"content": [{"type": "text", "text": json.dumps({
            "mood": "nostalgic", "emotion": "ignore-me", "energy_level": "low", "confidence": 5,
            "language": "marathi", "era_preference": "classic", "summary": "Taking it back.", "playlist_name": "Old Days"})}]}
        fake = mock.MagicMock()
        fake.__enter__.return_value.read.return_value = json.dumps(reply).encode()
        with mock.patch("urllib.request.urlopen", return_value=fake):
            result = analyze("take me back")
        self.assertEqual(result["engine"], "claude")
        self.assertEqual(result["mood"], "nostalgic")
        self.assertEqual(result["confidence"], 1.0)      # clamped
        self.assertNotEqual(result["emotion"], "ignore-me")  # invalid value rejected
        self.assertEqual(result["requested_language"], "marathi")


class EnrichMatchTests(TestCase):
    def test_pick_best_match_prefers_title_and_artist(self):
        song = Song(title="Tum Hi Ho", artist="Arijit Singh")
        results = [
            {"trackName": "Tum Hi Ho (Reprise)", "artistName": "Someone Else", "previewUrl": "http://x/1"},
            {"trackName": "Tum Hi Ho", "artistName": "Arijit Singh", "previewUrl": "http://x/2"},
            {"trackName": "Unrelated", "artistName": "Arijit Singh", "previewUrl": "http://x/3"},
            {"trackName": "Tum Hi Ho", "artistName": "Arijit Singh", "previewUrl": ""},
        ]
        self.assertEqual(pick_best_match(song, results)["previewUrl"], "http://x/2")
        self.assertIsNone(pick_best_match(song, [results[2]]))


class PlaybackTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_songs", verbosity=0)

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.client = APIClient()
        user = User.objects.create_user(username="p", email="p@example.com", password="test-pass-123")
        Profile.objects.create(user=user)
        token = self.client.post("/api/auth/login/", {"email": "p@example.com", "password": "test-pass-123"},
                                 format="json").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.song = Song.objects.get(title="Tum Hi Ho")

    def itunes_hit(self):
        return [{"trackName": "Tum Hi Ho", "artistName": "Arijit Singh", "previewUrl": "https://x/p.m4a",
                 "artworkUrl100": "https://x/100x100bb.jpg", "trackTimeMillis": 262000, "trackId": 5,
                 "collectionName": "Aashiqui 2", "trackViewUrl": "https://music.apple.com/x"}]

    def test_requires_login(self):
        self.client.credentials()
        self.assertEqual(self.client.get(f"/api/songs/{self.song.id}/playback/").status_code, 401)

    def test_itunes_metadata_does_not_become_preview_playback(self):
        with mock.patch("api.playback.fetch_itunes", return_value=self.itunes_hit()) as fetch:
            first = self.client.get(f"/api/songs/{self.song.id}/playback/").data
            second = self.client.get(f"/api/songs/{self.song.id}/playback/").data
        self.assertEqual(first["source"], "none")
        self.assertEqual(first["preview_url"], "")
        self.assertEqual(second["source"], "none")
        self.assertIn("youtube.com/results", first["external_url"])
        self.assertEqual(fetch.call_count, 1)  # looked up once, then stored in PostgreSQL
        self.song.refresh_from_db()
        self.assertEqual(self.song.duration, 262)
        self.assertIn("400x400", self.song.image_url)

    @override_settings(YOUTUBE_API_KEY="k")
    def test_youtube_preferred_when_available(self):
        with mock.patch("api.playback.find_video_id", return_value="abc123XYZ_-"), \
             mock.patch("api.playback.fetch_itunes", return_value=self.itunes_hit()):
            data = self.client.get(f"/api/songs/{self.song.id}/playback/").data
        self.assertEqual(data["source"], "youtube")
        self.assertEqual(data["youtube_id"], "abc123XYZ_-")
        self.assertEqual(data["preview_url"], "")  # iTunes previews are not a playback fallback
        self.assertEqual(data["external_url"], "https://www.youtube.com/watch?v=abc123XYZ_-")

    def test_nothing_found_and_offline(self):
        with mock.patch("api.playback.fetch_itunes", side_effect=OSError("offline")):
            data = self.client.get(f"/api/songs/{self.song.id}/playback/").data
        self.assertEqual(data["source"], "none")
        self.assertEqual(self.client.get("/api/songs/999999/playback/").status_code, 404)

    @override_settings(YOUTUBE_API_KEY="k")
    def test_youtube_quota_error_is_handled(self):
        import urllib.error
        err = urllib.error.HTTPError("u", 403, "quota", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=err), \
             mock.patch("api.playback.fetch_itunes", return_value=self.itunes_hit()):
            data = self.client.get(f"/api/songs/{self.song.id}/playback/").data
        self.assertEqual(data["source"], "none")  # opens YouTube search; never a 30s preview
        self.assertIn("youtube.com/results", data["external_url"])
