# services/token_service.py — Refresh token persistence
from datetime import datetime, timezone

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.tokens import hash_token
from models.refresh_token import RefreshToken


async def save_refresh_token(
    db: AsyncSession,
    user_id: str,
    refresh_token: str,
    session_id: str,
    expires_at: datetime,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> RefreshToken:
    token_hash = hash_token(refresh_token)
    record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        session_id=session_id,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def find_refresh_token(db: AsyncSession, refresh_token: str) -> RefreshToken | None:
    token_hash = hash_token(refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    return result.scalar_one_or_none()


async def is_valid_session(db: AsyncSession, user_id: str, session_id: str) -> bool:
    now = datetime.now(tz=timezone.utc)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.session_id == session_id,
            RefreshToken.is_active.is_(True),
            RefreshToken.expires_at > now,
        )
    )
    return result.scalar_one_or_none() is not None


async def revoke_session(db: AsyncSession, user_id: str, session_id: str) -> None:
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.session_id == session_id)
        .values(is_active=False)
    )
    await db.commit()


async def delete_current_refresh_token(db: AsyncSession, session_id: str) -> None:
    await db.execute(delete(RefreshToken).where(RefreshToken.session_id == session_id))
    await db.commit()


async def delete_all_refresh_tokens(db: AsyncSession, user_id: str) -> None:
    await db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))
    await db.commit()
