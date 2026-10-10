from decimal import Decimal

from app.database.session import SessionLocal
from app.models.network_metering_fee import NetworkMeteringFee
from app.models.network_operator import NetworkOperator


YEAR = 2026
ENERGY_TYPE = "gas"

METERING_FEES = {
    "Netz Niederösterreich GmbH": {
        "G4": Decimal("16.20"),
        "G6": Decimal("21.00"),
    },
    "Wiener Netze": {
        "G4": Decimal("16.20"),
        "G6": Decimal("21.00"),
    },
}


def seed() -> None:
    db = SessionLocal()

    try:
        for operator_name, meter_types in METERING_FEES.items():
            operator = (
                db.query(NetworkOperator)
                .filter(NetworkOperator.name == operator_name)
                .one_or_none()
            )

            if operator is None:
                print(f"⚠️ Operator not found: {operator_name}")
                continue

            for meter_type, annual_fee in meter_types.items():
                existing = (
                    db.query(NetworkMeteringFee)
                    .filter(
                        NetworkMeteringFee.network_operator_id == operator.id,
                        NetworkMeteringFee.year == YEAR,
                        NetworkMeteringFee.energy_type == ENERGY_TYPE,
                        NetworkMeteringFee.meter_type == meter_type,
                    )
                    .one_or_none()
                )

                if existing:
                    existing.annual_fee = annual_fee
                    action = "updated"
                else:
                    db.add(
                        NetworkMeteringFee(
                            network_operator_id=operator.id,
                            year=YEAR,
                            energy_type=ENERGY_TYPE,
                            meter_type=meter_type,
                            annual_fee=annual_fee,
                        )
                    )
                    action = "created"

                print(
                    f"{action}: {operator_name} | "
                    f"{ENERGY_TYPE} | {meter_type} | €{annual_fee}"
                )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()
