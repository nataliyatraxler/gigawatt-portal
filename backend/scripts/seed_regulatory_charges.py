from datetime import date
from decimal import Decimal

from app.database.session import SessionLocal
from app.models.regulatory_charge import RegulatoryCharge


CHARGES = [
    {
        "name": "Elektrizitätsabgabe",
        "calculation_type": "cent_per_kwh",
        "value": Decimal("0.820"),
        "network_level": None,
        "tariff_type": None,
        "network_area": None,
        "valid_from": date(2026, 1, 1),
        "valid_to": date(2026, 12, 31),
    },
    {
        "name": "Erneuerbaren-Förderbeitrag Grundbetrag",
        "calculation_type": "euro_per_year",
        "value": Decimal("3.796"),
        "network_level": 7,
        "tariff_type": "nicht_gemessen",
        "network_area": None,
        "valid_from": date(2026, 1, 1),
        "valid_to": date(2026, 12, 31),
    },
    {
        "name": "Erneuerbaren-Förderbeitrag Arbeit",
        "calculation_type": "cent_per_kwh",
        "value": Decimal("0.583"),
        "network_level": 7,
        "tariff_type": "nicht_gemessen",
        "network_area": None,
        "valid_from": date(2026, 1, 1),
        "valid_to": date(2026, 12, 31),
    },
    {
        "name": "Erneuerbaren-Förderbeitrag Netzverlust",
        "calculation_type": "cent_per_kwh",
        "value": Decimal("0.037"),
        "network_level": 7,
        "tariff_type": "nicht_gemessen",
        "network_area": None,
        "valid_from": date(2026, 1, 1),
        "valid_to": date(2026, 12, 31),
    },
    {
        "name": "Erneuerbaren-Förderpauschale",
        "calculation_type": "euro_per_year",
        "value": Decimal("19.020"),
        "network_level": 7,
        "tariff_type": None,
        "network_area": None,
        "valid_from": date(2026, 1, 1),
        "valid_to": date(2026, 12, 31),
    },
    {
        "name": "Gebrauchsabgabe",
        "calculation_type": "percent_of_network_tariff",
        "value": Decimal("7.000"),
        "network_level": None,
        "tariff_type": None,
        "network_area": "Wien",
        "valid_from": date(2026, 3, 1),
        "valid_to": None,
    },
]


def main():
    db = SessionLocal()

    try:
        created = 0
        updated = 0

        for data in CHARGES:
            existing = (
                db.query(RegulatoryCharge)
                .filter(
                    RegulatoryCharge.name == data["name"],
                    RegulatoryCharge.calculation_type
                    == data["calculation_type"],
                    RegulatoryCharge.network_level
                    == data["network_level"],
                    RegulatoryCharge.tariff_type
                    == data["tariff_type"],
                    RegulatoryCharge.network_area
                    == data["network_area"],
                    RegulatoryCharge.valid_from
                    == data["valid_from"],
                )
                .one_or_none()
            )

            if existing:
                existing.value = data["value"]
                existing.valid_to = data["valid_to"]
                updated += 1
            else:
                db.add(RegulatoryCharge(**data))
                created += 1

        db.commit()

        print(f"Created: {created}")
        print(f"Updated: {updated}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
