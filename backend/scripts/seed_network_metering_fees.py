from decimal import Decimal

from app.database.session import SessionLocal
from app.models.network_metering_fee import NetworkMeteringFee
from app.models.network_operator import NetworkOperator


YEAR = 2026
METER_TYPE = "standard"

# Nur verifizierte Messentgelte eintragen.
METERING_FEES = {
    "Wiener Netze": Decimal("26.16"),
    "Netz Niederösterreich GmbH": Decimal("26.16"),
    "Vorarlberger Energienetze GmbH": Decimal("19.20"),
    "Energie Klagenfurt GmbH": Decimal("28.80"),
    "Innsbrucker Kommunalbetriebe AG": Decimal("28.80"),
    "Netz Burgenland GmbH": Decimal("28.80"),
    "LINZ NETZ GmbH": Decimal("28.56"),
    "Salzburg Netz GmbH": Decimal("27.60"),
    "TINETZ-Tiroler Netze GmbH": Decimal("28.80"),
    "KNG-Kärnten Netz GmbH": Decimal("28.80"),
    "Energienetze Steiermark GmbH": Decimal("28.80"),
    "Energie Ried GmbH": Decimal("28.80"),
}


def main():
    db = SessionLocal()

    created = 0
    updated = 0
    unchanged = 0

    try:
        for operator_name, annual_fee in METERING_FEES.items():
            operator = (
                db.query(NetworkOperator)
                .filter(NetworkOperator.name == operator_name)
                .one_or_none()
            )

            if operator is None:
                raise RuntimeError(
                    f"Netzbetreiber nicht gefunden: {operator_name}"
                )

            fee = (
                db.query(NetworkMeteringFee)
                .filter(
                    NetworkMeteringFee.network_operator_id == operator.id,
                    NetworkMeteringFee.year == YEAR,
                    NetworkMeteringFee.meter_type == METER_TYPE,
                )
                .one_or_none()
            )

            if fee is None:
                db.add(
                    NetworkMeteringFee(
                        network_operator_id=operator.id,
                        year=YEAR,
                        meter_type=METER_TYPE,
                        annual_fee=annual_fee,
                    )
                )
                created += 1
                print(
                    f"CREATE | {operator.name} | "
                    f"{YEAR} | {METER_TYPE} | {annual_fee}"
                )
                continue

            if fee.annual_fee != annual_fee:
                print(
                    f"UPDATE | {operator.name} | "
                    f"{fee.annual_fee} -> {annual_fee}"
                )
                fee.annual_fee = annual_fee
                updated += 1
            else:
                unchanged += 1
                print(
                    f"OK     | {operator.name} | "
                    f"{YEAR} | {METER_TYPE} | {annual_fee}"
                )

        db.commit()

        print("\n===== RESULT =====")
        print("Created:", created)
        print("Updated:", updated)
        print("Unchanged:", unchanged)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
