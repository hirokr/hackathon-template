# core/deps.py — FastAPI dependency injectors
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import HTTPConnection

from core.config import settings
from core.database import get_db
from core.tokens import verify_access_token
from models.user import User
from services.token_service import is_valid_session
from services.user_service import get_user_by_id


def _extract_access_token(conn: HTTPConnection) -> str | None:
    auth_header = conn.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()

    token = conn.query_params.get("token") or conn.query_params.get("access_token")
    if token:
        return token

    return conn.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)


async def get_current_user(
    conn: HTTPConnection,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = _extract_access_token(conn)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await get_user_by_id(db, payload.user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    session_active = await is_valid_session(db, payload.user_id, payload.session_id or "")
    if not session_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    conn.state.user_id = payload.user_id
    conn.state.session_id = payload.session_id
    return user


def require_role(*roles: str):
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current_user
    return _check
