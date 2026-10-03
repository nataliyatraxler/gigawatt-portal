from sqlalchemy import and_

from app.database.session import SessionLocal
from app.models.network_operator import NetworkOperator
from app.models.usage_fee_rule import UsageFeeRule

from scripts.import_usage_fee_rules_2026 import (
    RULES,
    SOURCE,
    VALID_FROM,
)


def main() -> None:
    db = SessionLocal()

    created = 0
    updated = 0

    try:
        for rule in RULES:
            operator = (
                db.query(NetworkOperator)
                .filter(NetworkOperator.name == rule["operator"])
                .one()
            )

            gkz = rule["gkz"]
            supplier_scope = rule.get("supplier_scope", "all")
            include_metering_fee = rule.get(
                "include_metering_fee",
                True,
            )

            filters = [
                UsageFeeRule.network_operator_id == operator.id,
                UsageFeeRule.energy_type == "strom",
                UsageFeeRule.calculation_type == rule["type"],
                UsageFeeRule.supplier_scope == supplier_scope,
                UsageFeeRule.valid_from == VALID_FROM,
            ]

            if gkz is None:
                filters.append(UsageFeeRule.gkz.is_(None))
            else:
                filters.append(UsageFeeRule.gkz == gkz)

            # Für diesen Import gibt es noch keine Zuordnung
            # zu einem konkreten Lieferanten.
            filters.append(UsageFeeRule.provider_id.is_(None))

            existing = (
                db.query(UsageFeeRule)
                .filter(and_(*filters))
                .one_or_none()
            )

            if existing is None:
                db.add(
                    UsageFeeRule(
                        gkz=gkz,
                        network_operator_id=operator.id,
                        energy_type="strom",
                        calculation_type=rule["type"],
                        value=rule["value"],
                        provider_id=None,
                        supplier_scope=supplier_scope,
                        include_metering_fee=include_metering_fee,
                        valid_from=VALID_FROM,
                        valid_to=None,
                        source=SOURCE,
                    )
                )
                created += 1
            else:
                existing.value = rule["value"]
                existing.include_metering_fee = include_metering_fee
                existing.source = SOURCE
                existing.valid_to = None
                updated += 1

        db.commit()

        print("Import erfolgreich.")
        print("Created:", created)
        print("Updated:", updated)

        rows = (
            db.query(UsageFeeRule)
            .filter(
                UsageFeeRule.energy_type == "strom",
                UsageFeeRule.source == SOURCE,
            )
            .order_by(UsageFeeRule.id)
            .all()
        )

        print("Importierte Regeln:", len(rows))

        local_only = [
            row for row in rows
            if row.supplier_scope == "local_only"
        ]

        print("local_only:", len(local_only))

        for row in local_only:
            operator = db.get(
                NetworkOperator,
                row.network_operator_id,
            )
            print(
                "LOCAL_ONLY |",
                operator.name,
                "| GKZ:",
                row.gkz,
                "|",
                row.calculation_type,
                "|",
                row.value,
            )

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
