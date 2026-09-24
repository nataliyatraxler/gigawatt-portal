from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.calculator.network_costs import calculate_sne_network_costs
from app.calculator.regulatory_charges import calculate_regulatory_charges


MONEY = Decimal("0.01")
PERCENT = Decimal("100")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def calculate_total_network_costs(
    db: Session,
    *,
    calculation_date: date,
    year: int,
    network_area: str,
    network_operator_id: int,
    municipality: str | None,
    network_level: int,
    tariff_type: str,
    customer_type: str,
    consumption_kwh: Decimal,
    meter_type: str = "standard",
    vat_percent: Decimal = Decimal("20"),
) -> dict:
    network = calculate_sne_network_costs(
        db,
        year=year,
        network_area=network_area,
        network_operator_id=network_operator_id,
        network_level=network_level,
        tariff_type=tariff_type,
        consumption_kwh=consumption_kwh,
        meter_type=meter_type,
    )

    charges = calculate_regulatory_charges(
        db,
        calculation_date=calculation_date,
        consumption_kwh=consumption_kwh,
        customer_type=customer_type,
        network_tariff=network["total_network_tariff"],
        network_level=network_level,
        tariff_type=tariff_type,
        network_area=network_area,
        municipality=municipality,
    )

    complete = (
        network["total_network_tariff"] is not None
        and charges["total_charges"] is not None
    )

    if complete:
        net_total = (
            network["total_network_tariff"]
            + charges["total_charges"]
        )
        vat = net_total * vat_percent / PERCENT
        gross_total = net_total + vat
    else:
        net_total = None
        vat = None
        gross_total = None

    return {
        "network": network,
        "charges": charges,
        "net_total": (
            money(net_total)
            if net_total is not None
            else None
        ),
        "vat_percent": vat_percent,
        "vat": (
            money(vat)
            if vat is not None
            else None
        ),
        "gross_total": (
            money(gross_total)
            if gross_total is not None
            else None
        ),
        "complete": complete,
    }
