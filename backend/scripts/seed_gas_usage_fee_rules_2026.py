from datetime import date
from decimal import Decimal

from app.database.session import SessionLocal
from app.models.network_operator import NetworkOperator
from app.models.usage_fee_rule import UsageFeeRule


RULES = [
    {
        "operator": "Wiener Netze",
        "value": Decimal("6.0"),
        "valid_from": date(2026, 1, 1),
        "valid_to": date(2026, 2, 28),
    },
    {
        "operator": "Wiener Netze",
        "value": Decimal("7.0"),
        "valid_from": date(2026, 3, 1),
        "valid_to": date(2026, 12, 31),
    },
]


def seed() -> None:
    db = SessionLocal()

    try:
        for item in RULES:
            operator = (
                db.query(NetworkOperator)
                .filter(
                    NetworkOperator.name == item["operator"]
                )
                .one()
            )

            existing = (
                db.query(UsageFeeRule)
                .filter(
                    UsageFeeRule.network_operator_id == operator.id,
                    UsageFeeRule.energy_type == "gas",
                    UsageFeeRule.calculation_type
                    == "percent_of_network_tariff",
                    UsageFeeRule.gkz.is_(None),
                    UsageFeeRule.provider_id.is_(None),
                    UsageFeeRule.supplier_scope == "all",
                    UsageFeeRule.valid_from == item["valid_from"],
                )
                .one_or_none()
            )

            if existing:
                existing.value = item["value"]
                existing.valid_to = item["valid_to"]
                existing.include_metering_fee = True
                existing.source = "Wiener Netze 2026"
                action = "updated"
            else:
                db.add(
                    UsageFeeRule(
                        gkz=None,
                        network_operator_id=operator.id,
                        energy_type="gas",
                        calculation_type="percent_of_network_tariff",
                        value=item["value"],
                        provider_id=None,
                        supplier_scope="all",
                        include_metering_fee=True,
                        valid_from=item["valid_from"],
                        valid_to=item["valid_to"],
                        source="Wiener Netze 2026",
                    )
                )
                action = "created"

            print(
                f"{action}: {operator.name} | gas | "
                f"{item['value']}% | "
                f"{item['valid_from']} - {item['valid_to']}"
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()
