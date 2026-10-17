"""Local, dependency-free mood analyzer.

Reads free text (English, Hinglish/romanized Hindi-Marathi, Hindi/Marathi/Punjabi/Tamil/Telugu script,
emoji) and returns the emotion, a target mood, an energy level, the language the person is
writing in and any "old songs" / "new songs" / "Marathi songs" request found in the text.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

MOODS = ["happy", "sad", "calm", "energetic", "romantic", "angry", "focused", "party", "sleepy", "nostalgic", "chill"]

# emotion -> (terms, default mood). Terms of 5+ letters also match their longer forms (stress -> stressful).
EMOTIONS = {
    "joy": (["happy", "joyful", "great", "awesome", "wonderful", "delighted", "cheerful", "glad", "fantastic",
             "amazing", "elated", "blissful", "smiling", "laughing", "fun", "good", "positive", "bright", "sunny",
             "blessed", "grateful", "content", "khush", "khushi", "maza", "majja", "anand", "aanand"], "happy"),
    "sadness": (["sad", "depressed", "down", "blue", "unhappy", "melancholy", "heartbroken", "lonely", "miserable",
                 "crying", "cry", "tears", "grief", "sorrow", "gloomy", "hopeless", "empty", "hurt", "pain",
                 "devastated", "crushed", "broken", "breakup", "despair", "numb", "udaas", "udas", "dukhi", "dukh",
                 "rona", "heartbreak", "bad day", "lost"], "sad"),
    "anger": (["angry", "furious", "mad", "irritated", "annoyed", "rage", "frustrated", "hate", "resentful",
               "bitter", "outraged", "livid", "aggressive", "temper", "cranky", "fed up", "gussa", "gussey",
               "pissed"], "angry"),
    "stress": (["stress", "overwhelmed", "anxious", "anxiety", "worried", "tense", "pressure", "burnt out",
                "burned out", "exhausted", "drained", "overworked", "panic", "nervous", "restless", "uneasy",
                "tension", "thaka", "thak gaya", "thakla", "tired", "deadline", "exam"], "calm"),
    "love": (["love", "romantic", "affection", "caring", "tender", "passionate", "adore", "cherish", "smitten",
             "longing", "intimate", "loving", "valentine", "crush", "date", "wedding", "pyaar", "pyar", "ishq",
             "mohabbat", "prem", "girlfriend", "boyfriend", "anniversary", "together"], "romantic"),
    "fear": (["afraid", "scared", "fearful", "terrified", "frightened", "creeped out", "dread", "horror", "phobia",
             "alarmed", "paranoid", "threatened", "darr"], "calm"),
    "surprise": (["surprised", "shocked", "astonished", "startled", "unexpected", "wow", "incredible",
                 "unbelievable", "stunned", "speechless"], "energetic"),
    "excitement": (["excited", "thrilled", "pumped", "hyped", "energized", "eager", "enthusiastic", "stoked",
                   "buzzing", "can't wait", "cant wait", "amped", "fired up", "giddy"], "party"),
    "neutral": (["okay", "fine", "alright", "normal", "regular", "meh", "indifferent", "neutral", "so-so",
                "average", "ordinary"], "chill"),
}

# Activity / situation words that point straight at a mood.
CONTEXT_MOODS = {
    "calm": ["calm", "peaceful", "relax", "relaxing", "soothing", "gentle", "serene", "tranquil", "meditate",
             "meditation", "yoga", "unwind", "wind down", "sukoon", "shaant", "shanti", "soft"],
    "sleepy": ["sleep", "sleepy", "bedtime", "insomnia", "lullaby", "drowsy", "neend", "nap", "go to bed", "night"],
    "focused": ["study", "studying", "focus", "focused", "concentrate", "concentration", "work", "working", "coding",
                "homework", "reading", "productive", "deep work", "assignment", "revision"],
    "energetic": ["workout", "gym", "run", "running", "exercise", "cardio", "pump", "lifting", "energetic",
                  "sprint", "motivation", "motivated", "power", "hype"],
    "party": ["party", "dance", "dancing", "club", "celebrate", "celebration", "birthday", "dj", "naachna",
              "nachna", "friends", "festival", "garba", "dandiya", "wedding dance", "baraat", "turn up"],
    "nostalgic": ["nostalgic", "nostalgia", "memories", "remember", "throwback", "old days", "childhood",
                  "school days", "college days", "miss", "missing", "yaad", "yaadein", "retro", "vintage", "purane"],
    "romantic": ["romance", "candlelight", "dinner date", "propose", "proposal", "valentine"],
    "chill": ["chill", "chilling", "lofi", "lo-fi", "casual", "vibe", "vibes", "driving", "drive", "road trip",
              "roadtrip", "coffee", "weekend", "sunday", "rain", "rainy", "monsoon", "barish"],
    "happy": ["morning", "sunshine", "good vibes", "positive", "birthday wish", "holiday", "vacation", "trip"],
    "sad": ["alone", "missing someone", "breakup", "broke up", "cry", "goodbye", "funeral"],
    "angry": ["revenge", "rage", "fight", "furious", "anger"],
}

EMOJI_MOODS = {
    "happy": "😊😄😁😀🙂😃☀🌞", "sad": "😢😭😞😔💔🥺☹", "angry": "😡🤬😠👿", "romantic": "❤💕😍🥰😘💖💘💑",
    "party": "🎉🥳🪩🍻🕺💃", "sleepy": "😴🥱🌙💤", "calm": "😌🧘🌿☮", "energetic": "💪🔥⚡🏃🏋",
    "focused": "📚💻🎯🧠", "nostalgic": "📼🕰📷", "chill": "😎🛋☕🌧",
}

# Devanagari / Gurmukhi / Tamil / Telugu words (matched as substrings - combining marks break \\w).
SCRIPT_TERMS = {
    "happy": ["खुश", "आनंद", "मज़ा", "मजा", "ਖੁਸ਼", "மகிழ்", "సంతో"],
    "sad": ["उदास", "दुखी", "दुःख", "दुख", "ਦੁਖ", "ਉਦਾਸ", "சோக", "దుఃఖ", "బాధ"],
    "romantic": ["प्यार", "प्रेम", "इश्क", "ਪਿਆਰ", "காத", "ప్రేమ"],
    "angry": ["गुस्सा", "राग", "ਗੁੱਸਾ", "கோப", "కోప"],
    "calm": ["शांत", "सुकून", "ਸ਼ਾਂਤ", "அமைதி", "శాంతి"],
    "sleepy": ["नींद", "झोप"],
    "nostalgic": ["याद", "पुराने", "जुने"],
    "party": ["नाच", "पार्टी", "डान्स"],
    "calm_stress": ["थक", "ਥੱਕ", "అలస"],
}

ENERGY_LOW = ["peaceful", "calm", "relax", "relaxing", "soft", "gentle", "quiet", "slow", "sleepy", "tired",
              "rest", "unwind", "chill", "mellow", "soothing", "tranquil", "serene", "lazy", "cozy", "dreamy",
              "meditate", "ambient", "lo-fi", "lofi", "wind down", "bedtime", "sleep", "soulful", "sad", "lonely"]
ENERGY_HIGH = ["dance", "party", "energetic", "pump", "workout", "run", "running", "exercise", "celebrate", "hype",
               "loud", "fast", "beat", "jump", "sweat", "cardio", "gym", "upbeat", "intense", "wild", "banger",
               "turn up", "rage", "angry", "furious", "excited", "pumped"]

NEGATORS = {"not", "no", "never", "dont", "don't", "isnt", "isn't", "cant", "can't", "cannot", "nahi", "nahin",
            "na", "without", "hardly", "wasnt", "wasn't", "didnt", "didn't", "aint", "ain't"}
INTENSIFIERS = {"very", "really", "so", "extremely", "super", "totally", "too", "bahut", "bohot", "quite", "deeply"}

LANGUAGE_REQUESTS = {
    "hindi": ["hindi", "bollywood", "hindi songs", "hindi gaane", "hindi gane"],
    "marathi": ["marathi", "marathi songs", "marathi gaani", "marathi gane"],
    "punjabi": ["punjabi", "bhangra"],
    "tamil": ["tamil", "kollywood"],
    "telugu": ["telugu", "tollywood"],
    "english": ["english songs", "english music", "hollywood", "english"],
    "instrumental": ["instrumental", "no lyrics", "without lyrics"],
}
OLD_WORDS = ["old songs", "old song", "old music", "oldies", "old is gold", "classic", "classics", "vintage",
             "retro", "throwback", "purane", "purana", "70s", "80s", "90s", "60s", "golden era", "evergreen"]
NEW_WORDS = ["new songs", "new song", "latest", "trending", "new music", "new release", "recent", "viral",
             "top hits", "current hits", "naye", "2024", "2025", "2026"]

MARATHI_MARKERS = ["आहे", "मला", "तुला", "काय", "वाटतं", "वाटते", "गाणी", "गाणे", "झोप", "नाही रे", "आम्ही", "होतो",
                   "mala", "aahe", "ahe", "vatat", "gaani", "kay ", "tula", "amhi"]
HINDI_MARKERS = ["है", "मैं", "मुझे", "नहीं", "क्या", "हूँ", "गाना", "गाने", "mujhe", "hai ", "nahi", "mera", "gaana",
                 "gaane", "kya ", "hoon", "bahut"]

MOOD_PHRASES = {
    "happy": "bright and upbeat", "sad": "a bit low", "calm": "in need of calm", "energetic": "full of energy",
    "romantic": "in a romantic mood", "angry": "fired up", "focused": "ready to focus", "party": "ready to party",
    "sleepy": "ready to wind down", "nostalgic": "nostalgic", "chill": "relaxed",
}
PLAYLIST_NAMES = {
    "happy": "Bright Side", "sad": "Blue Hour", "calm": "Quiet Hours", "energetic": "Pulse", "romantic": "After Hours",
    "angry": "Let It Out", "focused": "Deep Work", "party": "Good Company", "sleepy": "Late Night",
    "nostalgic": "Old Photos", "chill": "Easy Listening",
}
MOOD_DEFAULT_EMOTION = {
    "happy": "joy", "sad": "sadness", "calm": "neutral", "energetic": "excitement", "romantic": "love",
    "angry": "anger", "focused": "neutral", "party": "excitement", "sleepy": "neutral", "nostalgic": "sadness",
    "chill": "neutral",
}


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9'\-]+", text.lower())


def _word_match(token: str, term: str) -> bool:
    if token == term:
        return True
    if len(term) >= 5 and token.startswith(term):
        return True
    if len(term) >= 3 and token in (term + "s", term + "ed", term + "ing", term + "ning", term + "d"):
        return True
    return False


def _find_terms(text: str, tokens: List[str], terms: List[str]) -> List[int]:
    """Return token positions (or -1 for multi-word phrases) where any term occurs."""
    hits = []
    for term in terms:
        if " " in term:
            if re.search(rf"(?<![a-z]){re.escape(term)}(?![a-z])", text):
                idx = text.find(term)
                hits.append(len(text[:idx].split()))
            continue
        for pos, token in enumerate(tokens):
            if _word_match(token, term):
                hits.append(pos)
    return hits


def detect_language(raw: str) -> tuple[str, float]:
    if re.search(r"[ऀ-ॿ]", raw):
        marathi = sum(raw.count(m) for m in MARATHI_MARKERS if re.search(r"[ऀ-ॿ]", m))
        hindi = sum(raw.count(m) for m in HINDI_MARKERS if re.search(r"[ऀ-ॿ]", m))
        return ("marathi", 0.8) if marathi > hindi else ("hindi", 0.8 if hindi else 0.6)
    if re.search(r"[਀-੿]", raw):
        return "punjabi", 0.85
    if re.search(r"[஀-௿]", raw):
        return "tamil", 0.85
    if re.search(r"[ఀ-౿]", raw):
        return "telugu", 0.85
    lowered = " " + raw.lower() + " "
    marathi = sum(lowered.count(" " + m.strip() + " ") for m in MARATHI_MARKERS if m.isascii())
    hindi = sum(lowered.count(" " + m.strip() + " ") for m in HINDI_MARKERS if m.isascii())
    if marathi > hindi and marathi:
        return "marathi", 0.6
    if hindi:
        return "hindi", 0.6
    return "english", 0.9


def _requested_language(lowered: str) -> str | None:
    for language, words in LANGUAGE_REQUESTS.items():
        for word in words:
            if re.search(rf"(?<![a-z]){re.escape(word)}(?![a-z])", lowered):
                return language
    return None


_SONG_NOUN = r"(?:songs?|music|hits|gaane|gaani|gane|tracks|melodies|numbers)"


def _requested_era(lowered: str) -> str | None:
    def has(words, adjective):
        if any(re.search(rf"(?<![a-z0-9]){re.escape(w)}(?![a-z])", lowered) for w in words):
            return True
        # "old marathi songs", "new punjabi hits": the adjective may be separated from the noun
        return bool(re.search(rf"\b(?:{adjective})\b(?:\s+[\w-]+){{0,2}}\s+{_SONG_NOUN}\b", lowered))
    old, new = has(OLD_WORDS, "old|older|oldest"), has(NEW_WORDS, "new|newer|latest|recent")
    if old and not new:
        return "classic"
    if new and not old:
        return "trending"
    return None


def analyze_mood(text: str) -> Dict[str, Any]:
    raw = (text or "").strip()
    if not raw:
        return _result("chill", "neutral", "medium", 0.5, "english", 0.9, [], None, None, None)

    lowered = raw.lower()
    cleaned = re.sub(r"[^\w\s'\-]", " ", lowered)
    tokens = _tokens(cleaned)
    mood_scores = {m: 0.0 for m in MOODS}
    emotion_scores = {e: 0.0 for e in EMOTIONS}
    keywords: List[str] = []

    for emotion, (terms, default_mood) in EMOTIONS.items():
        weight = 0.5 if emotion == "neutral" else 1.0
        for pos in _find_terms(cleaned, tokens, terms):
            prefix = tokens[max(0, pos - 3):pos] if pos >= 0 else []
            negated = any(t in NEGATORS for t in prefix)
            boosted = pos > 0 and tokens[pos - 1] in INTENSIFIERS
            value = weight * (1.5 if boosted else 1.0)
            if negated:
                if emotion == "joy":
                    emotion_scores["sadness"] += value
                    mood_scores["sad"] += value
                elif emotion in ("sadness", "anger", "stress", "fear"):
                    mood_scores["calm"] += value * 0.7
                continue
            emotion_scores[emotion] += value
            mood_scores[default_mood] += value
            if pos >= 0 and pos < len(tokens):
                keywords.append(tokens[pos])

    for mood, terms in CONTEXT_MOODS.items():
        for pos in _find_terms(cleaned, tokens, terms):
            mood_scores[mood] += 1.2
            if 0 <= pos < len(tokens):
                keywords.append(tokens[pos])

    for mood, symbols in EMOJI_MOODS.items():
        count = sum(raw.count(ch) for ch in symbols)
        if count:
            mood_scores[mood] += 1.5 * min(count, 3)
            keywords.append("emoji")

    for mood, terms in SCRIPT_TERMS.items():
        for term in terms:
            if term in raw:
                target = "calm" if mood == "calm_stress" else mood
                mood_scores[target] += 1.5
                if mood in ("happy", "sad", "romantic", "angry"):
                    emotion = {"happy": "joy", "sad": "sadness", "romantic": "love", "angry": "anger"}[mood]
                    emotion_scores[emotion] += 1.5
                if mood == "calm_stress":
                    emotion_scores["stress"] += 1.5

    ranked = sorted(mood_scores.items(), key=lambda kv: kv[1], reverse=True)
    top_mood, top_score = ranked[0]
    second_mood, second_score = ranked[1]
    total = sum(mood_scores.values())

    if top_score <= 0:
        top_mood, emotion, confidence, second_mood = "chill", "neutral", 0.5, None
    else:
        emotion = max(emotion_scores.items(), key=lambda kv: kv[1])[0] if any(emotion_scores.values()) \
            else MOOD_DEFAULT_EMOTION[top_mood]
        share = top_score / total
        margin = (top_score - second_score) / top_score
        confidence = min(0.97, 0.45 + 0.35 * share + 0.2 * margin + min(top_score, 4) * 0.02)
        if second_score < top_score * 0.5:
            second_mood = None

    low = len(_find_terms(cleaned, tokens, ENERGY_LOW))
    high = len(_find_terms(cleaned, tokens, ENERGY_HIGH))
    if low > high:
        energy = "low"
    elif high > low:
        energy = "high"
    else:
        energy = {"energetic": "high", "party": "high", "angry": "high", "calm": "low", "sleepy": "low",
                  "sad": "low"}.get(top_mood, "medium")

    language, language_conf = detect_language(raw)
    requested_language = _requested_language(lowered)
    era = _requested_era(lowered)
    seen = list(dict.fromkeys(keywords))[:6]
    return _result(top_mood, emotion, energy, round(confidence, 2), language, language_conf, seen,
                   second_mood, requested_language, era)


def _result(mood, emotion, energy, confidence, language, language_conf, keywords, secondary, requested_language, era):
    summary = f"You sound {MOOD_PHRASES.get(mood, 'relaxed')}, so I'm lining up {energy}-energy {mood} tracks."
    if requested_language and requested_language != "english":
        summary += f" Prioritising {requested_language.capitalize()} songs."
    if era == "classic":
        summary += " Leaning towards famous old songs."
    elif era == "trending":
        summary += " Leaning towards what's trending right now."
    return {
        "emotion": emotion,
        "mood": mood,
        "secondary_mood": secondary,
        "energy_level": energy,
        "confidence": confidence,
        "language": language,
        "language_confidence": language_conf,
        "requested_language": requested_language,
        "era_preference": era,
        "keywords": keywords,
        "summary": summary,
        "playlist_name": PLAYLIST_NAMES.get(mood, "Mood Session"),
        "engine": "local",
    }
