
import os
import requests
import streamlit as st

BASE_URL = (
    os.getenv("BACKEND_URL")
    or os.getenv("TRIBAL_API_BASE_URL")
    or "http://127.0.0.1:8000"
).rstrip("/")


def get_recent_chats(limit=10):
    token = st.session_state.get("auth_token")

    if not token:
        print("History error: Authentication token is missing.")
        return []

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/history/recent",
            params={"limit": limit},
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()
        data = response.json()

        return data.get("data", [])

    except requests.HTTPError as exc:
        print(
            f"History HTTP error: "
            f"{exc.response.status_code} - {exc.response.text}"
        )
        return []

    except requests.RequestException as exc:
        print(f"History connection error: {exc}")
        return []
