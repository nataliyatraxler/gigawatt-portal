import argparse
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from app.database.session import SessionLocal
from app.models.gas_network_tariff import GasNetworkTariff


NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}

AREAS = [
    ("Burgenland", 3),
    ("Kärnten", 14),
    ("Niederösterreich", 25),
    ("Oberösterreich", 36),
    ("Salzburg", 47),
    ("Steiermark", 58),
    ("Tirol", 69),
    ("Vorarlberg", 80),
    ("Wien", 91),
]

NE2_BANDS = [
    (0, 5_000_000),
    (5_000_000, 10_000_000),
    (10_000_000, 100_000_000),
    (100_000_000, 200_000_000),
    (200_000_000, 900_000_000),
    (900_000_000, None),
]

NE3_NOT_MEASURED_BANDS = [
    (0, 40_000),
    (40_000, 80_000),
    (80_000, 200_000),
    (200_000, None),
]

NE3_MEASURED_BANDS = [
    (0, 5_000_000),
    (5_000_000, 10_000_000),
    (10_000_000, 100_000_000),
    (100_000_000, None),
]


def column_name(number: int) -> str:
    result = ""

    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result

    return result


def load_cached_values(path: Path) -> dict[str, Decimal]:
    with ZipFile(path) as workbook:
        xml = workbook.read("xl/worksheets/sheet1.xml")

    root = ET.fromstring(xml)

    values: dict[str, Decimal] = {}

    for cell in root.findall(".//m:c", NS):
        reference = cell.attrib["r"]
        value = cell.find("m:v", NS)

        if value is None or value.text in (None, ""):
            continue

        try:
            values[reference] = Decimal(value.text).quantize(
                Decimal("0.000001")
            )
        except Exception:
            continue

    return values


def required_value(
    values: dict[str, Decimal],
    reference: str,
) -> Decimal:
    value = values.get(reference)

    if value is None:
        raise RuntimeError(
            f"Kein gespeicherter Excel-Wert in Zelle {reference}."
        )

    return value


def build_rows(
    values: dict[str, Decimal],
    year: int,
) -> list[dict]:
    rows: list[dict] = []

    for network_area, start_col in AREAS:

        # Netzebene 2
        # Excel rows 6-11:
        # Arbeitspreis Abs.5 / Abs.6a
        # Leistungspreis Abs.5 / Abs.6a
        for index, (lower, upper) in enumerate(NE2_BANDS):
            excel_row = 6 + index

            for variant, ap_offset, lp_offset in (
                ("abs5", 3, 7),
                ("abs6a", 4, 8),
            ):
                rows.append(
                    {
                        "year": year,
                        "network_area": network_area,
                        "network_level": 2,
                        "tariff_variant": variant,
                        "consumption_from_kwh": Decimal(lower),
                        "consumption_to_kwh": (
                            Decimal(upper)
                            if upper is not None
                            else None
                        ),
                        "arbeitspreis_cent_kwh": required_value(
                            values,
                            f"{column_name(start_col + ap_offset)}"
                            f"{excel_row}",
                        ),
                        "leistungspreis_cent_kwh_h": required_value(
                            values,
                            f"{column_name(start_col + lp_offset)}"
                            f"{excel_row}",
                        ),
                        "pauschale_cent_year": None,
                    }
                )

        # Netzebene 3:
        # nicht leistungsgemessen
        # Excel rows 18-21:
        # Arbeitspreis Abs.5 + Pauschale pro Jahr
        for index, (lower, upper) in enumerate(
            NE3_NOT_MEASURED_BANDS
        ):
            excel_row = 18 + index

            rows.append(
                {
                    "year": year,
                    "network_area": network_area,
                    "network_level": 3,
                    "tariff_variant": "nicht_leistungsgemessen",
                    "consumption_from_kwh": Decimal(lower),
                    "consumption_to_kwh": (
                        Decimal(upper)
                        if upper is not None
                        else None
                    ),
                    "arbeitspreis_cent_kwh": required_value(
                        values,
                        f"{column_name(start_col + 3)}{excel_row}",
                    ),
                    "leistungspreis_cent_kwh_h": None,
                    "pauschale_cent_year": required_value(
                        values,
                        f"{column_name(start_col + 7)}{excel_row}",
                    ),
                }
            )

        # Netzebene 3:
        # leistungsgemessen
        # Excel rows 23-26:
        # Arbeitspreis + Leistungspreis
        for index, (lower, upper) in enumerate(
            NE3_MEASURED_BANDS
        ):
            excel_row = 23 + index

            for variant, ap_offset, lp_offset in (
                ("abs5", 3, 8),
                ("abs6c", 4, 9),
            ):
                rows.append(
                    {
                        "year": year,
                        "network_area": network_area,
                        "network_level": 3,
                        "tariff_variant": variant,
                        "consumption_from_kwh": Decimal(lower),
                        "consumption_to_kwh": (
                            Decimal(upper)
                            if upper is not None
                            else None
                        ),
                        "arbeitspreis_cent_kwh": required_value(
                            values,
                            f"{column_name(start_col + ap_offset)}"
                            f"{excel_row}",
                        ),
                        "leistungspreis_cent_kwh_h": required_value(
                            values,
                            f"{column_name(start_col + lp_offset)}"
                            f"{excel_row}",
                        ),
                        "pauschale_cent_year": None,
                    }
                )

    return rows


def import_rows(rows: list[dict]) -> tuple[int, int]:
    db = SessionLocal()

    created = 0
    updated = 0

    try:
        for data in rows:
            existing = (
                db.query(GasNetworkTariff)
                .filter(
                    GasNetworkTariff.year == data["year"],
                    GasNetworkTariff.network_area
                    == data["network_area"],
                    GasNetworkTariff.network_level
                    == data["network_level"],
                    GasNetworkTariff.tariff_variant
                    == data["tariff_variant"],
                    GasNetworkTariff.consumption_from_kwh
                    == data["consumption_from_kwh"],
                )
                .one_or_none()
            )

            if existing is None:
                db.add(GasNetworkTariff(**data))
                created += 1
                continue

            existing.consumption_to_kwh = data[
                "consumption_to_kwh"
            ]
            existing.arbeitspreis_cent_kwh = data[
                "arbeitspreis_cent_kwh"
            ]
            existing.leistungspreis_cent_kwh_h = data[
                "leistungspreis_cent_kwh_h"
            ]
            existing.pauschale_cent_year = data[
                "pauschale_cent_year"
            ]

            updated += 1

        db.commit()

        return created, updated

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("xlsx", type=Path)

    parser.add_argument(
        "--dry-run",
        action="store_true",
    )

    args = parser.parse_args()

    if not args.xlsx.exists():
        raise SystemExit(
            f"Datei nicht gefunden: {args.xlsx}"
        )

    values = load_cached_values(args.xlsx)

    year_value = required_value(values, "A1")
    year = int(year_value)

    rows = build_rows(values, year)

    if len(rows) != 216:
        raise RuntimeError(
            f"Erwartet: 216 Datensätze, gefunden: {len(rows)}"
        )

    print("Jahr:", year)
    print("Netzbereiche:", len(AREAS))
    print("Datensätze:", len(rows))

    print()
    print("Kontrolle Burgenland NE3:")
    for row in rows:
        if (
            row["network_area"] == "Burgenland"
            and row["network_level"] == 3
            and row["tariff_variant"]
            == "nicht_leistungsgemessen"
        ):
            print(
                row["consumption_from_kwh"],
                "->",
                row["consumption_to_kwh"],
                "| AP:",
                row["arbeitspreis_cent_kwh"],
                "| Pauschale:",
                row["pauschale_cent_year"],
            )

    if args.dry_run:
        print()
        print("DRY RUN: keine Änderungen in der Datenbank.")
        return

    created, updated = import_rows(rows)

    print()
    print("Created:", created)
    print("Updated:", updated)
    print("Total:", created + updated)


if __name__ == "__main__":
    main()
