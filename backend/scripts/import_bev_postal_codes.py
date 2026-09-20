import csv
from pathlib import Path

from app.database.session import SessionLocal
from app.models.postal_code import PostalCode


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "Adresse_Relationale_Tabellen_Stichtagsdaten"
)

ADDRESS_FILE = DATA_DIR / "ADRESSE.csv"
LOCALITY_FILE = DATA_DIR / "ORTSCHAFT.csv"


def load_localities() -> dict[tuple[str, str], str]:
    localities = {}

    with LOCALITY_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            key = (row["GKZ"], row["OKZ"])
            localities[key] = row["ORTSNAME"].strip()

    return localities


def collect_postal_codes(
    localities: dict[tuple[str, str], str],
) -> set[tuple[str, str]]:
    postal_codes = set()

    with ADDRESS_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            postal_code = row["PLZ"].strip()
            key = (row["GKZ"], row["OKZ"])

            city = localities.get(key)

            if postal_code and city:
                postal_codes.add((postal_code, city))

    return postal_codes


def import_postal_codes() -> None:
    print("Loading BEV localities...")
    localities = load_localities()

    print(f"Loaded {len(localities)} localities.")

    print("Reading BEV addresses...")
    postal_codes = collect_postal_codes(localities)

    print(
        f"Found {len(postal_codes)} unique PLZ/Ort combinations."
    )

    db = SessionLocal()

    try:
        existing = {
            (item.postal_code, item.city)
            for item in db.query(PostalCode).all()
        }

        new_items = [
            PostalCode(
                postal_code=postal_code,
                city=city,
                network_operator_id=None,
            )
            for postal_code, city in sorted(postal_codes)
            if (postal_code, city) not in existing
        ]

        db.add_all(new_items)
        db.commit()

        print(f"Imported {len(new_items)} new postal code records.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    import_postal_codes()
