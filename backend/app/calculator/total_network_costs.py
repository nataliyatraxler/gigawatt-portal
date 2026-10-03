from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.calculator.network_costs import calculate_sne_network_costs
from app.calculator.regulatory_charges import calculate_regulatory_charges
from app.calculator.usage_fees import (
    calculate_usage_fee,
    get_usage_fee_rule,
)


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
    gkz: str | None,
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

    # Gebrauchsabgabe from the dedicated UsageFeeRule table.
    # At the network-cost stage we can calculate only rules that
    # do not depend on the supplier's energy price.
    usage_fee_rule = get_usage_fee_rule(
        db,
        calculation_date=calculation_date,
        network_operator_id=network_operator_id,
        gkz=gkz,
        energy_type="strom",
        provider_id=None,
    )

    usage_fee = Decimal("0.00")
    usage_fee_pending = False

    if usage_fee_rule is not None:
        if usage_fee_rule.calculation_type in {
            "cent_per_kwh",
            "percent_of_network_tariff",
        }:
            usage_fee = calculate_usage_fee(
                usage_fee_rule,
                consumption_kwh=consumption_kwh,
                energy_cost=Decimal("0"),
                network_tariff=network["total_network_tariff"],
                metering_cost=network["metering_cost"],
            )
        else:
            # percent_of_energy_cost and
            # percent_of_energy_and_network need the supplier tariff.
            usage_fee_pending = True

    # Remove any legacy Gebrauchsabgabe from RegulatoryCharge and
    # replace it with the dedicated UsageFeeRule result.
    base_charges = (
        charges["total_charges"]
        - charges["usage_fee"]
    )

    charges["usage_fee"] = money(usage_fee)
    charges["usage_fee_pending"] = usage_fee_pending
    charges["total_charges"] = money(
        base_charges + usage_fee
    )

    net_total = (
        network["total_network_tariff"]
        + charges["total_charges"]
    )

    vat = net_total * vat_percent / PERCENT
    gross_total = net_total + vat

    return {
        "network": network,
        "charges": charges,
        "net_total": money(net_total),
        "vat_percent": vat_percent,
        "vat": money(vat),
        "gross_total": money(gross_total),
    }
