from datetime import datetime, timezone
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from backend.config.settings import settings
from backend.database.connection import mongodb
from backend.auth.password_service import hash_password, verify_password
from backend.auth.token_service import create_access_token

def _users():
    if mongodb.database is None:
        raise RuntimeError("Database is not connected")
    return mongodb.database["users"]

def _public_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user["email"],
        "auth_provider": user.get("auth_provider", "email"),
        "created_at": user.get("created_at"),
    }

async def register_user(name: str, email: str, password: str) -> tuple[str, dict]:
    email = email.strip().lower()
    users = _users()
    if await users.find_one({"email": email}):
        raise ValueError("An account with this email already exists")
    now = datetime.now(timezone.utc)
    document = {
        "name": name.strip(),
        "email": email,
        "password_hash": hash_password(password),
        "auth_provider": "email",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    try:
        result = await users.insert_one(document)
    except DuplicateKeyError:
        raise ValueError("An account with this email already exists")
    document["_id"] = result.inserted_id
    user = _public_user(document)
    return create_access_token(user["id"], email), user

async def login_user(email: str, password: str) -> tuple[str, dict]:
    email = email.strip().lower()
    user = await _users().find_one({"email": email, "is_active": True})
    if not user or not user.get("password_hash") or not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid email or password")
    public = _public_user(user)
    return create_access_token(public["id"], email), public

async def login_with_google(raw_id_token: str) -> tuple[str, dict]:
    if not settings.GOOGLE_CLIENT_ID:
        raise RuntimeError("Google sign-in is not configured")
    try:
        info = google_id_token.verify_oauth2_token(
            raw_id_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except Exception as exc:
        raise ValueError("Google identity token could not be verified") from exc

    email = (info.get("email") or "").strip().lower()
    if not email or not info.get("email_verified"):
        raise ValueError("Google account email is not verified")

    users = _users()
    user = await users.find_one({"email": email})
    now = datetime.now(timezone.utc)
    if user is None:
        document = {
            "name": info.get("name") or email.split("@")[0],
            "email": email,
            "auth_provider": "google",
            "google_sub": info.get("sub"),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        result = await users.insert_one(document)
        document["_id"] = result.inserted_id
        user = document
    elif not user.get("is_active", True):
        raise ValueError("This account is disabled")
    else:
        await users.update_one(
            {"_id": user["_id"]},
            {"$set": {"google_sub": info.get("sub"), "updated_at": now}}
        )

    public = _public_user(user)
    return create_access_token(public["id"], email), public

async def get_user_by_id(user_id: str) -> dict | None:
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    user = await _users().find_one({"_id": oid, "is_active": True})
    return _public_user(user) if user else None
