from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    role: UserRole
    provider_id: int | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    role: UserRole | None = None
    provider_id: int | None = None
    active: bool | None = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    role: UserRole
    provider_id: int | None
    active: bool

    model_config = {
        "from_attributes": True
    }