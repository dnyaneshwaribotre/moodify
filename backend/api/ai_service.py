from .llm import llm_analyze
from .mood_analyzer import analyze_mood


def analyze(text: str) -> dict:
    """Mood analysis: Claude when configured, otherwise (or on any failure) the local analyzer."""
    result = analyze_mood(text)
    enhanced = llm_analyze(text)
    if enhanced:
        result.update(enhanced)
    return result
