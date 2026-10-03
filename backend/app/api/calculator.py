from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.calculator.address_network_costs import (
    calculate_network_costs_for_address,
)
from app.calculator.gas_network_costs import (
    calculate_gas_network_usage_costs,
    convert_gas_m3_to_kwh,
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
    if request.energy_type == "gas":
        if request.consumption_kwh is not None:
            consumption_kwh = Decimal(
                str(request.consumption_kwh)
            )
        elif request.consumption_m3 is not None:
            if request.gas_conversion_factor_kwh_m3 is None:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Bei Gasverbrauch in m³ ist der "
                        "Umrechnungsfaktor kWh/m³ erforderlich."
                    ),
                )

            consumption_kwh = convert_gas_m3_to_kwh(
                consumption_m3=Decimal(
                    str(request.consumption_m3)
                ),
                conversion_factor_kwh_m3=Decimal(
                    str(request.gas_conversion_factor_kwh_m3)
                ),
            )
        else:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Für Gas ist entweder consumption_kwh "
                    "oder consumption_m3 erforderlich."
                ),
            )

        if request.network_operator_id is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "network_operator_id ist für die "
                    "Gasberechnung erforderlich."
                ),
            )

        network = calculate_gas_network_usage_costs(
            db,
            year=request.calculation_date.year,
            network_operator_id=request.network_operator_id,
            consumption_kwh=consumption_kwh,
            network_level=request.network_level,
        )

        return {
            "energy_type": "gas",
            "calculation_status": "network_usage_only",
            "consumption_m3": request.consumption_m3,
            "gas_conversion_factor_kwh_m3": (
                request.gas_conversion_factor_kwh_m3
            ),
            "consumption_kwh": consumption_kwh,
            "network": network,
        }

    if request.consumption_kwh is None:
        raise HTTPException(
            status_code=422,
            detail="consumption_kwh ist für Strom erforderlich.",
        )

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
