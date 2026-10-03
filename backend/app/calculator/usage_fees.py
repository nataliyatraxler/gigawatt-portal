from datetime import date

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.usage_fee_rule import UsageFeeRule


def get_usage_fee_rule(
    db: Session,
    *,
    calculation_date: date,
    network_operator_id: int,
    gkz: str | None,
    energy_type: str = "strom",
    provider_id: int | None = None,
) -> UsageFeeRule | None:
    rules = (
        db.query(UsageFeeRule)
        .filter(
            UsageFeeRule.network_operator_id == network_operator_id,
            UsageFeeRule.energy_type == energy_type,
            UsageFeeRule.valid_from <= calculation_date,
            or_(
                UsageFeeRule.valid_to.is_(None),
                UsageFeeRule.valid_to >= calculation_date,
            ),
        )
        .all()
    )

    applicable_rules = []

    for rule in rules:
        if rule.supplier_scope == "all":
            applicable_rules.append(rule)
            continue

        if (
            rule.supplier_scope == "local_only"
            and provider_id is not None
            and rule.provider_id is not None
            and rule.provider_id == provider_id
        ):
            applicable_rules.append(rule)

    if gkz is not None:
        exact_rule = next(
            (
                rule
                for rule in applicable_rules
                if rule.gkz == gkz
            ),
            None,
        )

        if exact_rule is not None:
            return exact_rule

    return next(
        (
            rule
            for rule in applicable_rules
            if rule.gkz is None
        ),
        None,
    )


from decimal import Decimal, ROUND_HALF_UP


CENT = Decimal("100")
PERCENT = Decimal("100")
MONEY = Decimal("0.01")


def calculate_usage_fee(
    rule: UsageFeeRule | None,
    *,
    consumption_kwh: Decimal,
    energy_cost: Decimal,
    network_tariff: Decimal,
    metering_cost: Decimal,
) -> Decimal:
    if rule is None:
        return Decimal("0.00")

    network_basis = network_tariff

    if not rule.include_metering_fee:
        network_basis -= metering_cost

    if rule.calculation_type == "cent_per_kwh":
        result = (
            consumption_kwh
            * rule.value
            / CENT
        )

    elif rule.calculation_type == "percent_of_network_tariff":
        result = (
            network_basis
            * rule.value
            / PERCENT
        )

    elif rule.calculation_type == "percent_of_energy_cost":
        result = (
            energy_cost
            * rule.value
            / PERCENT
        )

    elif rule.calculation_type == "percent_of_energy_and_network":
        result = (
            (energy_cost + network_basis)
            * rule.value
            / PERCENT
        )

    else:
        raise ValueError(
            "Nicht unterstützte Berechnungsart "
            "für Gebrauchsabgabe: "
            f"{rule.calculation_type}"
        )

    return result.quantize(
        MONEY,
        rounding=ROUND_HALF_UP,
    )
