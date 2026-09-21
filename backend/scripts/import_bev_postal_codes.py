import csv
from collections import defaultdict
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
MUNICIPALITY_FILE = DATA_DIR / "GEMEINDE.csv"


def load_localities() -> dict[tuple[str, str], str]:
    localities = {}

    with LOCALITY_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            gkz = row["GKZ"].strip()
            okz = row["OKZ"].strip()
            city = row["ORTSNAME"].strip()

            if gkz and okz and city:
                localities[(gkz, okz)] = city

    return localities


def load_municipalities() -> dict[str, str]:
    municipalities = {}

    with MUNICIPALITY_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            gkz = row["GKZ"].strip()
            municipality = row["GEMEINDENAME"].strip()

            if gkz and municipality:
                municipalities[gkz] = municipality

    return municipalities


def collect_postal_codes(
    localities: dict[tuple[str, str], str],
    municipalities: dict[str, str],
) -> set[tuple[str, str, str, str]]:
    postal_codes = set()

    with ADDRESS_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            postal_code = row["PLZ"].strip()
            gkz = row["GKZ"].strip()
            okz = row["OKZ"].strip()

            city = localities.get((gkz, okz))
            municipality = municipalities.get(gkz)

            if (
                postal_code
                and city
                and gkz
                and municipality
            ):
                postal_codes.add(
                    (
                        postal_code,
                        city,
                        gkz,
                        municipality,
                    )
                )

    return postal_codes


def import_postal_codes() -> None:
    print("Loading BEV localities...")
    localities = load_localities()
    print(f"Loaded {len(localities)} localities.")

    print("Loading BEV municipalities...")
    municipalities = load_municipalities()
    print(f"Loaded {len(municipalities)} municipalities.")

    print("Reading BEV addresses...")
    postal_codes = collect_postal_codes(
        localities,
        municipalities,
    )

    print(
        f"Found {len(postal_codes)} unique "
        "PLZ/Ort/GKZ combinations."
    )

    bev_by_pair = defaultdict(list)

    for item in sorted(postal_codes):
        postal_code, city, gkz, municipality = item
        bev_by_pair[(postal_code, city)].append(
            (gkz, municipality)
        )

    db = SessionLocal()

    try:
        existing_rows = db.query(PostalCode).all()

        exact_existing = {
            (
                row.postal_code,
                row.city,
                row.gkz,
            ): row
            for row in existing_rows
            if row.gkz
        }

        legacy_by_pair = defaultdict(list)

        for row in existing_rows:
            if row.gkz is None:
                legacy_by_pair[
                    (row.postal_code, row.city)
                ].append(row)

        updated = 0
        created = 0

        for (
            postal_code,
            city,
        ), locations in sorted(bev_by_pair.items()):

            for gkz, municipality in locations:
                exact_key = (
                    postal_code,
                    city,
                    gkz,
                )

                existing = exact_existing.get(exact_key)

                if existing:
                    if existing.municipality != municipality:
                        existing.municipality = municipality
                        updated += 1
                    continue

                legacy_rows = legacy_by_pair.get(
                    (postal_code, city),
                    [],
                )

                if legacy_rows:
                    # Reuse the existing row so its ID and any
                    # existing network-operator mapping are preserved.
                    row = legacy_rows.pop(0)
                    row.gkz = gkz
                    row.municipality = municipality

                    exact_existing[exact_key] = row
                    updated += 1
                    continue

                row = PostalCode(
                    postal_code=postal_code,
                    city=city,
                    gkz=gkz,
                    municipality=municipality,
                    network_operator_id=None,
                )

                db.add(row)
                exact_existing[exact_key] = row
                created += 1

        db.commit()

        print(f"Updated existing records: {updated}")
        print(f"Created additional records: {created}")
        print("BEV postal code import finished.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    import_postal_codes()
