from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.calculator.filters import apply_tariff_filters
from app.calculator.formulas import (
    calculate_annual_cost_after_bonus,
    calculate_annual_cost_before_bonus,
    calculate_energy_cost,
)
from app.calculator.sorting import sort_by_annual_cost
from app.models.tariff import Tariff
from app.repositories.network import (
    get_network_operator_by_id,
    get_postal_codes,
)
from app.schemas.calculator import (
    TariffCalculationRequest,
    TariffCalculationResult,
)


def calculate_tariffs(
    db: Session,
    request: TariffCalculationRequest,
) -> list[TariffCalculationResult]:

    postal_codes = get_postal_codes(
        db,
        request.postal_code.strip(),
    )

    if not postal_codes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Für diese Postleitzahl wurde kein Netzbetreiber gefunden.",
        )

    if len(postal_codes) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Für diese Postleitzahl wurden mehrere Netzbetreiber gefunden.",
        )

    postal_code = postal_codes[0]

    network_operator = get_network_operator_by_id(
        db,
        postal_code.network_operator_id,
    )

    if not network_operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Netzbetreiber wurde nicht gefunden.",
        )

    if not network_operator.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Der Netzbetreiber ist derzeit nicht aktiv.",
        )

    query = db.query(Tariff)

    query = apply_tariff_filters(
    query=query,
    energy_type=request.energy_type,
    customer_type=request.customer_type,
    network_operator_id=network_operator.id,
    provider_id=request.provider_id,
)

    tariffs = query.all()

    results = []

    for tariff in tariffs:
        energy_cost = calculate_energy_cost(
            request.consumption_kwh,
            tariff.work_price_cent_kwh,
        )

        annual_cost_before_bonus = (
            calculate_annual_cost_before_bonus(
                tariff.base_price_year,
                energy_cost,
            )
        )

        annual_cost_after_bonus = (
            calculate_annual_cost_after_bonus(
                annual_cost_before_bonus,
                tariff.bonus,
            )
        )

        results.append(
            TariffCalculationResult(
                tariff_id=tariff.id,
                provider_id=tariff.provider_id,
                tariff_name=tariff.name,

                postal_code=postal_code.postal_code,
                city=postal_code.city,
                network_operator_id=network_operator.id,
                network_operator_name=network_operator.name,

                consumption_kwh=request.consumption_kwh,

                base_price_year=round(
                    tariff.base_price_year,
                    2,
                ),
                work_price_cent_kwh=tariff.work_price_cent_kwh,
                bonus=round(
                    tariff.bonus,
                    2,
                ),

                energy_cost=round(
                    energy_cost,
                    2,
                ),
                annual_cost_before_bonus=round(
                    annual_cost_before_bonus,
                    2,
                ),
                annual_cost_after_bonus=round(
                    annual_cost_after_bonus,
                    2,
                ),
            )
        )

    return sort_by_annual_cost(results)