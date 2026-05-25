# core/tokens.py — JWT helpers
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from jose import JWTError, jwt

from core.config import settings


@dataclass(frozen=True)
class TokenPayload:
    user_id: str
    session_id: str | None


def _parse_duration(value: str, default_minutes: int) -> timedelta:
    raw = value.strip().lower()
    if not raw:
        return timedelta(minutes=default_minutes)
    unit = raw[-1]
    amount = raw[:-1]
    try:
        qty = int(amount)
    except ValueError:
        return timedelta(minutes=default_minutes)

    if unit == "m":
        return timedelta(minutes=qty)
    if unit == "h":
        return timedelta(hours=qty)
    if unit == "d":
        return timedelta(days=qty)
    return timedelta(minutes=default_minutes)


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _encode(payload: dict, secret: str, expires_in: timedelta) -> str:
    issued_at = _now()
    exp = issued_at + expires_in
    data = {**payload, "iat": int(issued_at.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(data, secret, algorithm="HS256")


def create_access_token(user_id: str, session_id: str) -> str:
    expires = _parse_duration(settings.JWT_EXPIRES_IN, default_minutes=5)
    return _encode({"sub": user_id, "sid": session_id, "type": "access"}, settings.JWT_SECRET, expires)


def create_refresh_token(user_id: str) -> str:
    expires = _parse_duration(settings.REFRESH_JWT_EXPIRES_IN, default_minutes=60 * 24 * 15)
    return _encode({"sub": user_id, "type": "refresh"}, settings.REFRESH_JWT_SECRET, expires)


def verify_access_token(token: str) -> TokenPayload | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except JWTError:
        return None
    if payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    session_id = payload.get("sid")
    if not user_id or not session_id:
        return None
    return TokenPayload(user_id=user_id, session_id=session_id)


def verify_refresh_token(token: str) -> TokenPayload | None:
    try:
        payload = jwt.decode(token, settings.REFRESH_JWT_SECRET, algorithms=["HS256"])
    except JWTError:
        return None
    if payload.get("type") != "refresh":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return TokenPayload(user_id=user_id, session_id=None)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session_id() -> str:
    return secrets.token_urlsafe(32)


def access_cookie_max_age() -> int:
    return int(_parse_duration(settings.JWT_EXPIRES_IN, default_minutes=5).total_seconds())


def refresh_cookie_max_age() -> int:
    return int(_parse_duration(settings.REFRESH_JWT_EXPIRES_IN, default_minutes=60 * 24 * 15).total_seconds())
