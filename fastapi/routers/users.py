# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.deps import get_current_user, require_role
from models.user import User
from schemas.user import UserOut, UserUpdate
from services import user_service

router = APIRouter()


@router.get("/", response_model=list[UserOut], dependencies=[Depends(require_role("admin"))])
async def list_users(db: AsyncSession = Depends(get_db)):
    return await user_service.get_all_users(db)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(require_role("admin"))])
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut, dependencies=[Depends(require_role("admin"))])
async def update_user(user_id: str, body: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user_service.update_user(db, user, body.model_dump(exclude_none=True))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_role("admin"))])
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user_service.delete_user(db, user)


@router.get("/health")
async def health():
    return {"status": "ok"}
