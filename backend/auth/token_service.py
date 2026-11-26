from datetime import datetime, timedelta, timezone
import jwt
from jwt import InvalidTokenError
from backend.config.settings import settings

ALGORITHM = "HS256"

def create_access_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": expires,
        "iss": settings.AUTH_TOKEN_ISSUER,
    }
    return jwt.encode(payload, settings.AUTH_SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.AUTH_SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=settings.AUTH_TOKEN_ISSUER,
        )
    except InvalidTokenError as exc:
        raise ValueError("Invalid or expired access token") from exc
