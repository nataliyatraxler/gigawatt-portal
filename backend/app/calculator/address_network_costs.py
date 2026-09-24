from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.calculator.total_network_costs import (
    calculate_total_network_costs,
)
from app.repositories.network import (
    get_network_operator_by_id,
    get_postal_code_by_id,
)
from app.services.network_operator_resolver import (
    resolve_network_operator,
)


def calculate_network_costs_for_address(
    db: Session,
    *,
    postal_code_id: int,
    network_operator_id: int | None = None,
    street_code: str | None = None,
    calculation_date: date,
    year: int,
    customer_type: str,
    network_level: int,
    tariff_type: str,
    consumption_kwh: Decimal,
    meter_type: str = "standard",
    vat_percent: Decimal = Decimal("20"),
) -> dict:

    postal_code = get_postal_code_by_id(
        db,
        postal_code_id,
    )

    if not postal_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PLZ/Ort wurde nicht gefunden.",
        )

    if network_operator_id is not None:
        network_operator = get_network_operator_by_id(
            db,
            network_operator_id,
        )

        if not network_operator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Der ausgewählte Netzbetreiber wurde nicht gefunden.",
            )
    else:
        network_operator = resolve_network_operator(
            db,
            postal_code=postal_code,
            street_code=street_code,
        )

        if not network_operator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Für diesen Ort wurde kein Netzbetreiber gefunden.",
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

    costs = calculate_total_network_costs(
        db,
        calculation_date=calculation_date,
        year=year,
        network_area=network_operator.sne_network_area,
        network_operator_id=network_operator.id,
        municipality=postal_code.municipality,
        network_level=network_level,
        customer_type=customer_type,
        tariff_type=tariff_type,
        consumption_kwh=consumption_kwh,
        meter_type=meter_type,
        vat_percent=vat_percent,
    )

    return {
        "address": {
            "postal_code_id": postal_code.id,
            "postal_code": postal_code.postal_code,
            "city": postal_code.city,
        },
        "network_operator": {
            "id": network_operator.id,
            "name": network_operator.name,
            "code": network_operator.code,
            "sne_network_area": network_operator.sne_network_area,
        },
        **costs,
    }
