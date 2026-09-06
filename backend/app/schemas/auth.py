from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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