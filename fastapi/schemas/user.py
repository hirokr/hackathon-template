# schemas/user.py — Pydantic request / response schemas
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
    avatar_url: str | None = None
    user_body_image_url: str | None = None
    age: int | None = None
    gender: str | None = None
    location: str | None = None
    interests: list[str] | None = None
    email_verified: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = None
    avatar_url: str | None = None
    user_body_image_url: str | None = None
    age: int | None = None
    gender: str | None = None
    location: str | None = None
    interests: list[str] | None = None
    ethnicity: str | None = None
    role: str | None = None
