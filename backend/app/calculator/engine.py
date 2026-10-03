from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.calculator.filters import apply_tariff_filters
from app.calculator.formulas import (
    calculate_annual_cost_after_bonus,
    calculate_annual_cost_before_bonus,
    calculate_energy_cost,
)
from app.calculator.sorting import sort_by_annual_cost
from app.calculator.total_network_costs import calculate_total_network_costs
from app.calculator.usage_fees import (
    calculate_usage_fee,
    get_usage_fee_rule,
)
from app.models.tariff import Tariff
from app.repositories.network import (
    get_network_operator_by_id,
    get_postal_code_by_id,
)
from app.schemas.calculator import (
    TariffCalculationRequest,
    TariffCalculationResult,
)


def calculate_tariffs(
    db: Session,
    request: TariffCalculationRequest,
) -> list[TariffCalculationResult]:

    postal_code = get_postal_code_by_id(
        db,
        request.postal_code_id,
    )

    if not postal_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PLZ/Ort wurde nicht gefunden.",
        )

    network_operator = get_network_operator_by_id(
        db,
        request.network_operator_id,
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

    if not network_operator.sne_network_area:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Für den Netzbetreiber ist kein SNE-Netzgebiet hinterlegt.",
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

    network_costs = calculate_total_network_costs(
        db,
        calculation_date=request.calculation_date,
        year=request.calculation_date.year,
        network_area=network_operator.sne_network_area,
        network_operator_id=network_operator.id,
        municipality=postal_code.municipality,
        gkz=postal_code.gkz,
        network_level=request.network_level,
        tariff_type=request.tariff_type,
        customer_type=request.customer_type,
        consumption_kwh=Decimal(
            str(request.consumption_kwh)
        ),
        meter_type=request.meter_type,
    )

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

        usage_fee_rule = get_usage_fee_rule(
            db,
            calculation_date=request.calculation_date,
            network_operator_id=network_operator.id,
            gkz=postal_code.gkz,
            energy_type=request.energy_type,
            provider_id=tariff.provider_id,
        )

        usage_fee = calculate_usage_fee(
            usage_fee_rule,
            consumption_kwh=Decimal(
                str(request.consumption_kwh)
            ),
            energy_cost=Decimal(
                str(annual_cost_after_bonus)
            ),
            network_tariff=network_costs[
                "network"
            ]["total_network_tariff"],
            metering_cost=network_costs[
                "network"
            ]["metering_cost"],
        )

        total_annual_cost = (
            Decimal(str(annual_cost_after_bonus))
            + network_costs["network"]["total_network_tariff"]
            + network_costs["charges"]["total_charges"]
            + usage_fee
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

                network_tariff=float(
                    network_costs[
                        "network"
                    ]["total_network_tariff"]
                ),
                regulatory_charges=float(
                    network_costs[
                        "charges"
                    ]["total_charges"]
                ),
                usage_fee=float(
                    usage_fee
                ),
                total_annual_cost=float(
                    total_annual_cost
                ),
            )
        )

    return sort_by_annual_cost(results)
