from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.calculator.address_network_costs import (
    calculate_network_costs_for_address,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.calculator import (
    NetworkCostCalculationRequest,
    TariffCalculationRequest,
    TariffCalculationResult,
)
from app.services.calculator import calculate_tariffs


router = APIRouter(
    prefix="/calculator",
    tags=["tarifrechner"],
)


@router.post(
    "/tariffs",
    response_model=list[TariffCalculationResult],
)
def calculate_available_tariffs(
    request: TariffCalculationRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return calculate_tariffs(
        db,
        request,
    )


@router.post("/network-costs")
def calculate_network_costs(
    request: NetworkCostCalculationRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return calculate_network_costs_for_address(
        db,
        postal_code_id=request.postal_code_id,
        network_operator_id=request.network_operator_id,
        street_code=request.street_code,
        calculation_date=request.calculation_date,
        year=request.calculation_date.year,
        network_level=request.network_level,
        tariff_type=request.tariff_type,
        consumption_kwh=Decimal(
            str(request.consumption_kwh)
        ),
        customer_type=request.customer_type,
        meter_type=request.meter_type,
    )
