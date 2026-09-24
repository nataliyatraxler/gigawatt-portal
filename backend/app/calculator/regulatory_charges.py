from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.regulatory_charge import RegulatoryCharge


CENT = Decimal("100")
PERCENT = Decimal("100")
MONEY = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def get_charge(
    db: Session,
    *,
    name: str,
    calculation_date: date,
    network_level: int | None = None,
    tariff_type: str | None = None,
    customer_type: str | None = None,
    network_area: str | None = None,
) -> RegulatoryCharge:
    query = db.query(RegulatoryCharge).filter(
        RegulatoryCharge.name == name,
        RegulatoryCharge.valid_from <= calculation_date,
        or_(
            RegulatoryCharge.valid_to.is_(None),
            RegulatoryCharge.valid_to >= calculation_date,
        ),
    )

    if network_level is not None:
        query = query.filter(
            or_(
                RegulatoryCharge.network_level.is_(None),
                RegulatoryCharge.network_level == network_level,
            )
        )

    if tariff_type is not None:
        query = query.filter(
            or_(
                RegulatoryCharge.tariff_type.is_(None),
                RegulatoryCharge.tariff_type == tariff_type,
            )
        )

    if network_area is not None:
        query = query.filter(
            or_(
                RegulatoryCharge.network_area.is_(None),
                RegulatoryCharge.network_area == network_area,
            )
        )
    if customer_type is not None:
        query = query.filter(
            RegulatoryCharge.customer_type == customer_type
        )

    return query.one()


def calculate_regulatory_charges(
    db: Session,
    *,
    calculation_date: date,
    consumption_kwh: Decimal,
    customer_type: str,
    network_tariff: Decimal,
    network_level: int,
    tariff_type: str,
    network_area: str,
    municipality: str | None = None,
) -> dict:
    electricity_tax = get_charge(
        db,
        name="Elektrizitätsabgabe",
        calculation_date=calculation_date,
        customer_type=customer_type,
    )

    efb_base = get_charge(
        db,
        name="Erneuerbaren-Förderbeitrag Grundbetrag",
        calculation_date=calculation_date,
        network_level=network_level,
        tariff_type=tariff_type,
    )

    efb_work = get_charge(
        db,
        name="Erneuerbaren-Förderbeitrag Arbeit",
        calculation_date=calculation_date,
        network_level=network_level,
        tariff_type=tariff_type,
    )

    efb_loss = get_charge(
        db,
        name="Erneuerbaren-Förderbeitrag Netzverlust",
        calculation_date=calculation_date,
        network_level=network_level,
        tariff_type=tariff_type,
    )

    renewable_flat_fee = get_charge(
        db,
        name="Erneuerbaren-Förderpauschale",
        calculation_date=calculation_date,
        network_level=network_level,
    )

    usage_fee = (
        db.query(RegulatoryCharge)
        .filter(
            RegulatoryCharge.name == "Gebrauchsabgabe",
            RegulatoryCharge.network_area == municipality,
            RegulatoryCharge.valid_from <= calculation_date,
            or_(
                RegulatoryCharge.valid_to.is_(None),
                RegulatoryCharge.valid_to >= calculation_date,
            ),
        )
        .one_or_none()
    )

    electricity_tax_cost = (
        consumption_kwh * electricity_tax.value / CENT
    )

    renewable_contribution = (
        efb_base.value
        + consumption_kwh * efb_work.value / CENT
        + consumption_kwh * efb_loss.value / CENT
    )

    renewable_flat_fee_cost = renewable_flat_fee.value

    usage_fee_cost = (
        network_tariff * usage_fee.value / PERCENT
        if usage_fee
        else Decimal("0")
    )

    total = (
        electricity_tax_cost
        + renewable_contribution
        + renewable_flat_fee_cost
        + usage_fee_cost
    )

    return {
        "electricity_tax": money(electricity_tax_cost),
        "renewable_contribution": money(renewable_contribution),
        "renewable_flat_fee": money(renewable_flat_fee_cost),
        "usage_fee": money(usage_fee_cost),
        "total_charges": money(total),
    }
