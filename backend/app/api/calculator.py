from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.calculator.address_network_costs import (
    calculate_network_costs_for_address,
)
from app.calculator.gas_network_costs import (
    calculate_gas_network_usage_costs,
    convert_gas_m3_to_kwh,
)
from app.calculator.regulatory_charges import (
    calculate_gas_regulatory_charges,
)
from app.calculator.usage_fees import (
    calculate_usage_fee,
    get_usage_fee_rule,
)
from app.database.session import get_db
from app.models.commission import Commission
from app.models.user import User, UserRole
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



@router.get("/tariffs/{tariff_id}/commission")
def get_tariff_commission(
    tariff_id: int,
    calculation_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {
        UserRole.AGENT,
        UserRole.SUPERADMIN,
    }:
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung für Provisionsdaten.",
        )

    commission = (
        db.query(Commission)
        .filter(
            Commission.tariff_id == tariff_id,
            Commission.active.is_(True),
            Commission.valid_from <= calculation_date,
            (
                Commission.valid_to.is_(None)
                | (Commission.valid_to >= calculation_date)
            ),
        )
        .order_by(
            Commission.valid_from.desc(),
            Commission.id.desc(),
        )
        .first()
    )

    if commission is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Für diesen Tarif ist keine gültige "
                "Provision hinterlegt."
            ),
        )

    return {
        "tariff_id": tariff_id,
        "agent_commission": float(
            commission.agent_commission
        ),
        "valid_from": commission.valid_from,
        "valid_to": commission.valid_to,
    }


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
            customer_type=request.customer_type,
            meter_type=request.meter_type,
        )

        if request.gas_conversion_factor_kwh_m3 is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Für die Berechnung der Erdgasabgabe ist der "
                    "Umrechnungsfaktor kWh/m³ erforderlich."
                ),
            )

        gas_conversion_factor = Decimal(
            str(request.gas_conversion_factor_kwh_m3)
        )

        regulatory = calculate_gas_regulatory_charges(
            db,
            calculation_date=request.calculation_date,
            consumption_kwh=consumption_kwh,
            conversion_factor_kwh_m3=gas_conversion_factor,
        )

        usage_fee_rule = get_usage_fee_rule(
            db,
            calculation_date=request.calculation_date,
            network_operator_id=request.network_operator_id,
            gkz=None,
            energy_type="gas",
        )

        usage_fee = calculate_usage_fee(
            usage_fee_rule,
            consumption_kwh=consumption_kwh,
            energy_cost=Decimal("0"),
            network_tariff=network["network_usage_subtotal"],
            metering_cost=network["metering_fee"],
        )

        net_total = (
            network["network_usage_subtotal"]
            + regulatory["total_charges"]
            + usage_fee
        )

        vat_rate = Decimal("20")
        vat = (
            net_total * vat_rate / Decimal("100")
        ).quantize(Decimal("0.01"))

        gross_total = (
            net_total + vat
        ).quantize(Decimal("0.01"))

        return {
            "energy_type": "gas",
            "calculation_status": "complete",
            "consumption_m3": request.consumption_m3,
            "gas_conversion_factor_kwh_m3": gas_conversion_factor,
            "consumption_kwh": consumption_kwh,
            "network": network,
            "regulatory_charges": regulatory,
            "usage_fee": usage_fee,
            "usage_fee_rate_percent": (
                usage_fee_rule.value
                if usage_fee_rule is not None
                else Decimal("0")
            ),
            "net_total": net_total,
            "vat_rate_percent": vat_rate,
            "vat": vat,
            "gross_total": gross_total,
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
