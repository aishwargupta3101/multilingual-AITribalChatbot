import re

WEATHER_PATTERNS = [
    r"\bweather\b",
    r"\btemperature\b",
    r"\bforecast\b",
    r"\bwill it rain\b",
    r"\bis it raining\b",
    r"\bhumidity\b",
]
TIME_PATTERNS = [
    r"\bwhat time is it\b",
    r"\bcurrent time\b",
    r"\btime right now\b",
    r"\blocal time\b",
]
DATE_PATTERNS = [
    r"\bwhat date is it\b",
    r"\btoday's date\b",
    r"\bcurrent date\b",
    r"\bwhat day is it\b",
]

def detect_realtime_intent(message: str) -> str | None:
    """Return the requested real-time tool, or None."""
    text = message.lower().strip()
    if any(re.search(p, text) for p in WEATHER_PATTERNS):
        return "weather"
    if any(re.search(p, text) for p in TIME_PATTERNS):
        return "time"
    if any(re.search(p, text) for p in DATE_PATTERNS):
        return "date"

    return None
