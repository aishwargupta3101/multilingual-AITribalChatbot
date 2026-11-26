from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from backend.auth.auth_models import RegisterRequest, LoginRequest, GoogleLoginRequest, TokenResponse
from backend.auth.auth_service import register_user, login_user, login_with_google, get_user_by_id
from backend.auth.token_service import decode_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
_bearer = HTTPBearer(auto_error=False)

def _token_response(token: str, user: dict) -> TokenResponse:
    return TokenResponse(access_token=token, user=user)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    try:
        token, user = await register_user(payload.name, str(payload.email), payload.password)
        return _token_response(token, user)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    try:
        token, user = await login_user(str(payload.email), payload.password)
        return _token_response(token, user)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

@router.post("/google", response_model=TokenResponse)
async def google_login(payload: GoogleLoginRequest):
    try:
        token, user = await login_with_google(payload.id_token)
        return _token_response(token, user)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        claims = decode_access_token(credentials.credentials)
        user = await get_user_by_id(claims.get("sub", ""))
    except ValueError:
        user = None
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user

@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return {"user": user}
