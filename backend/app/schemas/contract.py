from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ContractBase(BaseModel):
    contract_number: str
    customer_id: int
    provider_id: int
    tariff_id: int

    status: str = "draft"

    annual_consumption: int | None = None

    start_date: date | None = None
    end_date: date | None = None

    supplier_commission: Decimal | None = None
    agent_commission: Decimal | None = None
    company_profit: Decimal | None = None

    signed: bool = False
    cancelled: bool = False

    notes: str | None = None


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    contract_number: str | None = None
    customer_id: int | None = None
    provider_id: int | None = None
    tariff_id: int | None = None

    status: str | None = None
    annual_consumption: int | None = None

    start_date: date | None = None
    end_date: date | None = None

    supplier_commission: Decimal | None = None
    agent_commission: Decimal | None = None
    company_profit: Decimal | None = None

    signed: bool | None = None
    cancelled: bool | None = None

    notes: str | None = None


class ContractRead(ContractBase):
    id: int
    agent_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)