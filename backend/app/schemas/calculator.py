from pydantic import BaseModel, Field


class TariffCalculationRequest(BaseModel):
    postal_code: str = Field(min_length=4, max_length=10)

    consumption_kwh: float = Field(gt=0)

    energy_type: str
    customer_type: str

    provider_id: int | None = None


class TariffCalculationResult(BaseModel):
    tariff_id: int
    provider_id: int
    tariff_name: str

    postal_code: str
    city: str
    network_operator_id: int
    network_operator_name: str

    consumption_kwh: float

    base_price_year: float
    work_price_cent_kwh: float
    bonus: float

    energy_cost: float
    annual_cost_before_bonus: float
    annual_cost_after_bonus: float