from datetime import date
from pydantic import BaseModel


class TariffBase(BaseModel):
    provider_id: int
    name: str

    energy_type: str
    customer_type: str

    base_price_year: float
    work_price_cent_kwh: float
    night_price_cent_kwh: float | None = None

    bonus: float = 0

    contract_months: int | None = None
    price_guarantee_months: int | None = None

    green_energy: bool = False
    digital_signature: bool = False

    active: bool = True

    valid_from: date | None = None
    valid_to: date | None = None


class TariffCreate(TariffBase):
    pass


class TariffUpdate(BaseModel):
    name: str | None = None

    energy_type: str | None = None
    customer_type: str | None = None

    base_price_year: float | None = None
    work_price_cent_kwh: float | None = None
    night_price_cent_kwh: float | None = None

    bonus: float | None = None

    contract_months: int | None = None
    price_guarantee_months: int | None = None

    green_energy: bool | None = None
    digital_signature: bool | None = None

    active: bool | None = None

    valid_from: date | None = None
    valid_to: date | None = None


class TariffResponse(TariffBase):
    id: int

    model_config = {
        "from_attributes": True
    }