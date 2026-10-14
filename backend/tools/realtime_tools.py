from datetime import datetime
from zoneinfo import ZoneInfo
import httpx

GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

async def get_location(place: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            GEOCODING_URL,
            params={
                "name": place,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )
        response.raise_for_status()
        results = response.json().get("results", [])
    if not results:
        raise ValueError(f"Location not found: {place}")
    return results[0]

async def get_weather(place: str) -> dict:
    """Fetch current weather from Open-Meteo."""
    location = await get_location(place)
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            WEATHER_URL,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "precipitation,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto",
            },
        )
        response.raise_for_status()
        data = response.json()
    return {
        "place": location["name"],
        "country": location.get("country", ""),
        "timezone": location.get("timezone", "UTC"),
        "current": data.get("current", {}),
        "units": data.get("current_units", {}),
        "source": "Open-Meteo",
    }

def get_current_time(timezone: str = "Asia/Kolkata") -> dict:
    """Return the current time for an IANA timezone."""
    now = datetime.now(ZoneInfo(timezone))
    return {
        "timezone": timezone,
        "time": now.strftime("%I:%M:%S %p"),
        "date": now.strftime("%d %B %Y"),
    }
