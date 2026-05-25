# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.deps import get_current_user, require_role
from models.user import User
from schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from schemas.user import UserOut, UserUpdate
from services import token_service, user_service
from core.security import hash_password, verify_password
from core.tokens import create_session_id
from services.email_tasks import send_password_reset_email_task, send_verification_email_task
from core.config import settings

router = APIRouter()


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


@router.post("/resend-verification-email", response_model=MessageResponse)
async def resend_verification_email(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump(exclude_none=True)
    data.pop("role", None)
    return await user_service.update_user(db, current_user, data)


@router.post("/me/change-password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.password_hash:
        raise HTTPException(status_code=400, detail="User account does not have a password set")
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    current_user.password_hash = hash_password(body.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}


@router.post("/change-password", response_model=MessageResponse)
async def change_password_alias(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await change_password(body, current_user, db)


@router.delete("/me", response_model=MessageResponse)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await user_service.soft_delete_user(db, current_user)
    await token_service.delete_all_refresh_tokens(db, current_user.id)
    return {"message": "Account deleted successfully"}


@router.delete("/delete-account", response_model=MessageResponse)
async def delete_account_alias(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await delete_me(current_user, db)


@router.get("/", response_model=list[UserOut], dependencies=[Depends(require_role("admin"))])
async def list_users(db: AsyncSession = Depends(get_db)):
    return await user_service.get_all_users(db)


@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(require_role("admin"))])
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_id(db, user_id)
    if not user or user.deleted_at is not None:
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
    await user_service.soft_delete_user(db, user)
    await token_service.delete_all_refresh_tokens(db, user.id)
