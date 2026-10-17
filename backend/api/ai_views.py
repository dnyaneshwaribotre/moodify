from collections import Counter

from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .ai_service import analyze
from .llm import llm_enabled
from .mood_analyzer import MOODS, MOOD_PHRASES
from .models import MoodHistory
from .recommender import build_session

ENERGIES = {"low", "medium", "high"}


class MoodAnalyzeView(APIView):
    """AI tool 1: turn free text (words, emoji, Hindi/Marathi...) into mood, energy, language and era."""
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai"

    def post(self, request):
        text = request.data.get("text", "")
        if not isinstance(text, str) or not text.strip():
            return Response({"text": "Please provide text to analyze."}, status=400)
        if len(text) > 2000:
            return Response({"text": "Please keep the description under 2000 characters."}, status=400)
        return Response(analyze(text))


class RecommendView(APIView):
    """AI tool 2: ranked mood session with trending + classic sections and a reason for every song."""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai"

    def post(self, request):
        data = request.data
        analysis = None
        mood = data.get("mood")
        if mood not in MOODS:
            text = data.get("text", "")
            if not isinstance(text, str) or not text.strip():
                return Response({"mood": "Send a valid mood or some text to analyze."}, status=400)
            analysis = analyze(text[:2000])
            mood = analysis["mood"]
        energy = data.get("energy_level") if data.get("energy_level") in ENERGIES else "medium"
        language = data.get("language") if isinstance(data.get("language"), str) else None
        era = data.get("era_preference") if data.get("era_preference") in ("classic", "trending") else None
        if analysis:
            energy = analysis["energy_level"]
            language = analysis.get("requested_language") or (
                analysis["language"] if analysis["language"] != "english" else None)
            era = analysis.get("era_preference")
        language = language or "indian"
        sections = build_session(request.user, mood, energy, language, era)
        return Response({
            "mood": mood, "energy_level": energy, "language": language, "era_preference": era,
            "analysis": analysis, "sections": sections,
            "total": sum(len(section["songs"]) for section in sections),
        })


class InsightsView(APIView):
    """AI tool 3: a short, personal read of the user's recent moods plus a time-of-day suggestion."""

    def get(self, request):
        recent = list(MoodHistory.objects.filter(user=request.user)[:30])
        hour = timezone.localtime().hour
        if hour < 6:
            suggested, when = "sleepy", "late night"
        elif hour < 11:
            suggested, when = "happy", "morning"
        elif hour < 17:
            suggested, when = "focused", "afternoon"
        elif hour < 22:
            suggested, when = "chill", "evening"
        else:
            suggested, when = "calm", "night"
        counts = Counter(item.detected_mood for item in recent)
        top = counts.most_common(1)[0][0] if counts else None
        if top:
            message = (f"You've mostly been {MOOD_PHRASES.get(top, top)} lately "
                       f"({counts[top]} of your last {len(recent)} sessions).")
        else:
            message = "Describe your first mood to start getting personal insights."
        return Response({
            "top_mood": top, "mood_counts": dict(counts), "message": message,
            "suggested_mood": suggested, "suggestion_reason": f"A {suggested} session suits the {when}.",
            "llm_enabled": llm_enabled(),
        })
