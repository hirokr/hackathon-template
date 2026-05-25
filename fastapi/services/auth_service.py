# services/auth_service.py — Auth business logic
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password, verify_password
from models.user import User
from services.user_service import get_user_by_email


async def register_user(db: AsyncSession, email: str, password: str, name: str) -> User:
    existing = await get_user_by_email(db, email)
    if existing:
        raise ValueError("Email already registered")
    user = User(email=email, name=name, password_hash=hash_password(password), role="user")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(db, email)
    if not user or not user.password_hash:
        raise ValueError("Invalid credentials")
    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")
    return user
