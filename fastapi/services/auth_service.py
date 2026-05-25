# services/auth_service.py — Auth business logic
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password, verify_password
from core.tokens import (
    create_access_token,
    create_refresh_token,
    create_session_id,
    refresh_cookie_max_age,
)
from models.user import User
from services import token_service, user_service


def _refresh_expiry() -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(seconds=refresh_cookie_max_age())


async def register_user(db: AsyncSession, email: str, password: str, name: str) -> tuple[User, str]:
    existing = await user_service.get_user_by_email(db, email)
    if existing:
        if existing.deleted_at is not None:
            raise ValueError("Account is deleted")
        if existing.password_hash and existing.password_hash.strip():
            raise ValueError("User already exists")
        verification_token = existing.verification_token or create_session_id()
        existing.verification_token = verification_token
        existing.password_hash = hash_password(password)
        existing.name = name or existing.name
        await db.commit()
        await db.refresh(existing)
        return existing, verification_token

    verification_token = create_session_id()
    user = User(
        email=email.strip().lower(),
        name=name.strip(),
        password_hash=hash_password(password),
        verification_token=verification_token,
        email_verified=False,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user, verification_token


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await user_service.get_user_by_email(db, email)
    if not user or not user.password_hash:
        raise ValueError("Invalid credentials")
    if user.deleted_at is not None or not user.is_active:
        raise ValueError("Account is inactive")
    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")
    return user


async def issue_tokens(
    db: AsyncSession,
    user: User,
    user_agent: str | None,
    ip_address: str | None,
) -> dict:
    session_id = create_session_id()
    access_token = create_access_token(user.id, session_id)
    refresh_token = create_refresh_token(user.id)
    expires_at = _refresh_expiry()
    await token_service.save_refresh_token(
        db,
        user_id=user.id,
        refresh_token=refresh_token,
        session_id=session_id,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "session_id": session_id,
    }


async def refresh_tokens(
    db: AsyncSession,
    refresh_token: str,
    user_agent: str | None,
    ip_address: str | None,
) -> dict:
    from core.tokens import verify_refresh_token

    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise ValueError("Invalid refresh token")

    stored = await token_service.find_refresh_token(db, refresh_token)
    if not stored or not stored.is_active or stored.user_id != payload.user_id:
        raise ValueError("Invalid refresh token")
    if stored.expires_at <= datetime.now(tz=timezone.utc):
        raise ValueError("Refresh token expired")

    await token_service.revoke_session(db, payload.user_id, stored.session_id)

    new_session_id = create_session_id()
    access_token = create_access_token(payload.user_id, new_session_id)
    new_refresh_token = create_refresh_token(payload.user_id)
    expires_at = _refresh_expiry()

    await token_service.save_refresh_token(
        db,
        user_id=payload.user_id,
        refresh_token=new_refresh_token,
        session_id=new_session_id,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "session_id": new_session_id,
    }


async def create_google_user(db: AsyncSession, profile: dict[str, Any]) -> User:
    email = (profile.get("email") or "").strip().lower()
    if not email:
        raise ValueError("Google profile email missing")

    name = (profile.get("name") or email.split("@")[0]).strip()
    avatar = profile.get("picture")
    google_id = profile.get("sub")

    existing = await user_service.get_user_by_email(db, email)
    if existing:
        if existing.deleted_at is not None:
            raise ValueError("Account is deleted")
        existing.name = existing.name or name
        existing.avatar_url = existing.avatar_url or avatar
        existing.email_verified = True
        existing.is_active = True
        existing.oauth_provider = "google"
        existing.oauth_id = google_id
        await db.commit()
        await db.refresh(existing)
        return existing

    user = User(
        email=email,
        name=name,
        avatar_url=avatar,
        password_hash=None,
        email_verified=True,
        is_active=True,
        oauth_provider="google",
        oauth_id=google_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
