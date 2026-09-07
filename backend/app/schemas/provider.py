from pydantic import BaseModel, EmailStr


class ProviderCreate(BaseModel):
    name: str
    website: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class ProviderUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    active: bool | None = None


class ProviderResponse(BaseModel):
    id: int
    name: str
    website: str | None
    email: EmailStr | None
    phone: str | None
    active: bool

    model_config = {
        "from_attributes": True
    }