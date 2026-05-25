# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from authlib.integrations.starlette_client import OAuth
from core.config import settings
from core.database import get_db
from schemas.auth import LoginRequest, MessageResponse, RegisterRequest
from schemas.user import UserOut
from services import auth_service, user_service

router = APIRouter()

# ── OAuth setup ───────────────────────────────────────────────────────────────
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
oauth.register(
    name="facebook",
    client_id=settings.META_CLIENT_ID,
    client_secret=settings.META_CLIENT_SECRET,
    access_token_url="https://graph.facebook.com/oauth/access_token",
    authorize_url="https://www.facebook.com/dialog/oauth",
    api_base_url="https://graph.facebook.com/",
    client_kwargs={"scope": "email"},
)


# ── Local auth (session-based) ────────────────────────────────────────────────
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.register_user(db, body.email, body.password, body.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    request.session["user_id"] = user.id
    return user


@router.post("/login", response_model=UserOut)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.authenticate_user(db, body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    request.session["user_id"] = user.id
    return user


@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}


# ── Google OAuth ──────────────────────────────────────────────────────────────
@router.get("/google")
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    profile = token.get("userinfo")
    user = await user_service.get_user_by_email(db, profile["email"])
    if not user:
        from models.user import User
        user = User(email=profile["email"], name=profile["name"], google_id=profile["sub"], role="user")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    request.session["user_id"] = user.id
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=settings.CLIENT_URL)


# ── Facebook / Meta OAuth ─────────────────────────────────────────────────────
@router.get("/facebook")
async def facebook_login(request: Request):
    return await oauth.facebook.authorize_redirect(request, settings.META_REDIRECT_URI)


@router.get("/facebook/callback")
async def facebook_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.facebook.authorize_access_token(request)
    resp = await oauth.facebook.get("me?fields=id,name,email", token=token)
    profile = resp.json()
    user = await user_service.get_user_by_email(db, profile.get("email", ""))
    if not user:
        from models.user import User
        user = User(email=profile.get("email", ""), name=profile["name"], facebook_id=profile["id"], role="user")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    request.session["user_id"] = user.id
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=settings.CLIENT_URL)
