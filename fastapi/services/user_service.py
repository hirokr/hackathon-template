# services/user_service.py — User CRUD business logic
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


def _normalize_email(email: str) -> str:
    return email.strip().lower()


async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User)
        .where(User.deleted_at.is_(None))
        .order_by(User.created_at.desc())
    )
    return list(result.scalars().all())


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    return await db.get(User, user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    normalized = _normalize_email(email)
    result = await db.execute(
        select(User).where(func.lower(User.email) == normalized)
    )
    return result.scalar_one_or_none()


async def get_user_by_verification_token(db: AsyncSession, token: str) -> User | None:
    result = await db.execute(
        select(User).where(User.verification_token == token, User.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user: User, data: dict) -> User:
    for key, value in data.items():
        if value is not None:
            setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_password(db: AsyncSession, user: User, password_hash: str) -> None:
    user.password_hash = password_hash
    await db.commit()


async def verify_user_email(db: AsyncSession, user: User, token: str) -> User:
    if user.verification_token != token:
        raise ValueError("Invalid verification token")
    user.email_verified = True
    user.is_active = True
    user.verification_token = None
    await db.commit()
    await db.refresh(user)
    return user


async def soft_delete_user(db: AsyncSession, user: User) -> None:
    user.deleted_at = datetime.now(tz=timezone.utc)
    user.is_active = False
    await db.commit()
