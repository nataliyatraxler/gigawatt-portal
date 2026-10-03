from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class TariffCalculationRequest(BaseModel):
    postal_code_id: int = Field(gt=0)

    network_operator_id: int = Field(gt=0)

    consumption_kwh: float = Field(gt=0)

    energy_type: str
    customer_type: str

    calculation_date: date

    network_level: int = Field(default=7, ge=1, le=7)
    tariff_type: str = "nicht_gemessen"
    meter_type: str = "standard"

    provider_id: int | None = None


class TariffCalculationResult(BaseModel):
    tariff_id: int
    provider_id: int
    provider_name: str
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

    network_tariff: float
    regulatory_charges: float
    usage_fee: float
    total_annual_cost: float


class NetworkCostCalculationRequest(BaseModel):
    postal_code_id: int = Field(gt=0)

    network_operator_id: int | None = Field(default=None, gt=0)

    street_code: str | None = None

    energy_type: Literal["strom", "gas"] = "strom"

    consumption_kwh: float | None = Field(default=None, gt=0)

    consumption_m3: float | None = Field(default=None, gt=0)

    gas_conversion_factor_kwh_m3: float | None = Field(
        default=None,
        gt=0,
    )

    customer_type: Literal["privat", "gewerbe"]

    calculation_date: date

    network_level: int = Field(default=7, ge=1, le=7)

    tariff_type: str = "nicht_gemessen"

    meter_type: str = "standard"
