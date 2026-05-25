# routers/auth.py
from urllib.parse import urlencode

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from core.deps import get_current_user
from core.security import hash_password
from core.tokens import access_cookie_max_age, refresh_cookie_max_age, create_session_id
from models.user import User
from schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from schemas.user import UserOut
from services import auth_service, token_service, user_service
from services.email_tasks import (
    send_password_reset_email_task,
    send_verification_email_task,
    send_welcome_email_task,
)

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


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        settings.ACCESS_TOKEN_COOKIE_NAME,
        access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=access_cookie_max_age(),
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    response.set_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=refresh_cookie_max_age(),
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME, path="/")
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME, path="/")


def _get_refresh_token(request: Request, body: RefreshRequest) -> str | None:
    return body.refresh_token or request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)


# ── Local auth (JWT-based) ───────────────────────────────────────────────────
@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        user, verification_token = await auth_service.register_user(db, body.email, body.password, body.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tokens = await auth_service.issue_tokens(
        db,
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    send_verification_email_task.delay(
        user.email,
        user.name,
        f"{settings.FRONTEND_URL}/auth/verify-email?token={verification_token}",
        1440,
    )

    response = JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "user": UserOut.model_validate(user).model_dump(),
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
        },
    )
    _set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return response


@router.post("/signin", response_model=AuthResponse)
async def signin(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.authenticate_user(db, body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tokens = await auth_service.issue_tokens(
        db,
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    response = JSONResponse(
        content={
            "user": UserOut.model_validate(user).model_dump(),
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
        }
    )
    _set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, request: Request, db: AsyncSession = Depends(get_db)):
    refresh_token = _get_refresh_token(request, body)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        tokens = await auth_service.refresh_tokens(
            db,
            refresh_token,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    response = JSONResponse(
        content={
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
        }
    )
    _set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return response


@router.get("/refresh", response_model=TokenResponse)
async def refresh_get(request: Request, db: AsyncSession = Depends(get_db)):
    return await refresh(RefreshRequest(), request, db)


@router.post("/signout", response_model=MessageResponse)
async def signout(request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    session_id = getattr(request.state, "session_id", None)
    if session_id:
        await token_service.revoke_session(db, current_user.id, session_id)
        await token_service.delete_current_refresh_token(db, session_id)
    else:
        await token_service.delete_all_refresh_tokens(db, current_user.id)

    response = JSONResponse(content={"message": "Signed out"})
    _clear_auth_cookies(response)
    return response


@router.get("/signout", response_model=MessageResponse)
async def signout_get(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await signout(request, current_user, db)


# ── Google OAuth ─────────────────────────────────────────────────────────────
@router.get("/google")
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    profile = token.get("userinfo") or {}
    if not profile:
        profile = await oauth.google.userinfo(token=token)

    try:
        user = await auth_service.create_google_user(db, profile)
    except ValueError:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/signin?error=google_oauth_failed")

    tokens = await auth_service.issue_tokens(
        db,
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    send_welcome_email_task.delay(
        user.email,
        user.name,
        f"{settings.FRONTEND_URL}",
    )

    query = urlencode(
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatarUrl": user.avatar_url or "",
            "emailVerified": str(user.email_verified).lower(),
            "isActive": str(user.is_active).lower(),
            "userBodyImageUrl": user.user_body_image_url or "",
            "age": user.age or "",
            "gender": user.gender or "",
            "location": user.location or "",
            "interests": ",".join(user.interests or []),
            "accessToken": tokens["access_token"],
            "refreshToken": tokens["refresh_token"],
        }
    )

    redirect_url = f"{settings.FRONTEND_URL}/api/auth/google/callback?{query}"
    response = RedirectResponse(url=redirect_url)
    _set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return response


@router.get("/google/failure")
async def google_failure():
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/signin?error=google_oauth_failed")


# ── Email verification / password reset ─────────────────────────────────────
@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_email(db, body.email)
    if user:
        token = create_session_id()
        user.verification_token = token
        await db.commit()
        send_password_reset_email_task.delay(
            user.email,
            user.name,
            f"{settings.FRONTEND_URL}/auth/reset-pass?token={token}",
            60,
        )
    return {"message": "If that email is registered, a reset link has been sent"}


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_verification_token(db, body.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.password_hash = hash_password(body.new_password)
    user.verification_token = None
    await db.commit()
    return {"message": "Password reset successfully"}


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    user = None
    if body.user_id:
        user = await user_service.get_user_by_id(db, body.user_id)
    if not user:
        user = await user_service.get_user_by_verification_token(db, body.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    await user_service.verify_user_email(db, user, body.token)
    return {"message": "Email verified successfully"}


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.email_verified:
        raise HTTPException(status_code=400, detail="Email is already verified")

    token = create_session_id()
    current_user.verification_token = token
    await db.commit()

    send_verification_email_task.delay(
        current_user.email,
        current_user.name,
        f"{settings.FRONTEND_URL}/auth/verify-email?token={token}",
        1440,
    )
    return {"message": "Verification email sent successfully"}


