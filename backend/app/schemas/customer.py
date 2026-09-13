from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerBase(BaseModel):
    customer_type: str

    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None

    email: EmailStr | None = None
    phone: str | None = None

    country: str = "Österreich"
    postal_code: str | None = None
    city: str | None = None
    street: str | None = None
    house_number: str | None = None

    active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_type: str | None = None

    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None

    email: EmailStr | None = None
    phone: str | None = None

    country: str | None = None
    postal_code: str | None = None
    city: str | None = None
    street: str | None = None
    house_number: str | None = None

    active: bool | None = None


class CustomerRead(CustomerBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)