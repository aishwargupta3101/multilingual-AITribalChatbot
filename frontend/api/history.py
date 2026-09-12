import requests
import os

BASE_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)
def get_recent_chats(limit=10):
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/history/recent",
            params={
                "limit": limit
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get(
            "data",
            []
        )
    except Exception as e:
        print(
            f"History error: {e}"
        )
        return []