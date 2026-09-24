import argparse
from collections import Counter, defaultdict

from app.database.session import SessionLocal
from app.models.network_operator import NetworkOperator
from app.models.network_operator_identifier import NetworkOperatorIdentifier
from app.models.sne_tariff import SneTariff


YEAR = 2026

# Standardfall:
# Für die meisten Strom-Netzbetreiber entspricht der SNE-Netzbereich
# dem im ZPN-Verzeichnis angegebenen Bundesland.
#
# Ausnahmen werden über den ZPN-Präfix definiert, nicht über den Namen.

AREA_OVERRIDES = {
    # Netzbereich Linz
    "AT003100": "Linz",  # LINZ NETZ GmbH
    "AT003310": "Linz",  # Elektrizitätswerk Perg GmbH
    "AT003460": "Linz",  # Ebner Strom GmbH
    "AT002900": "Linz",  # E-Werk Sarmingstein
    "AT002910": "Linz",  # Elektrizitätswerk Clam

    # Eigene Netzbereiche
    "AT007100": "Klagenfurt",  # Energie Klagenfurt GmbH
    "AT008100": "Graz",        # Stromnetz Graz GmbH
    "AT005100": "Innsbruck",   # Innsbrucker Kommunalbetriebe AG

    # Im aktuellen Import eventuell nicht vorhanden,
    # aber für zukünftige vollständige ZPN-Daten vorbereitet.
    "AT006230": "Kleinwalsertal",

    # Laut SNE-V Netzbereich Oberösterreich,
    # obwohl der Betreiber im ZPN-Verzeichnis Steiermark führt.
    "AT008850": "Oberösterreich",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Änderungen tatsächlich in die Datenbank schreiben.",
    )
    args = parser.parse_args()

    db = SessionLocal()

    try:
        valid_areas = {
            area
            for (area,) in (
                db.query(SneTariff.network_area)
                .filter(SneTariff.year == YEAR)
                .distinct()
                .all()
            )
        }

        rows = (
            db.query(NetworkOperatorIdentifier, NetworkOperator)
            .join(
                NetworkOperator,
                NetworkOperator.id
                == NetworkOperatorIdentifier.network_operator_id,
            )
            .filter(
                NetworkOperatorIdentifier.energy_type == "Strom",
                NetworkOperatorIdentifier.active.is_(True),
                NetworkOperator.active.is_(True),
            )
            .order_by(NetworkOperatorIdentifier.zpn_prefix)
            .all()
        )

        assignments = []
        areas_per_operator = defaultdict(set)

        for identifier, operator in rows:
            area = AREA_OVERRIDES.get(
                identifier.zpn_prefix,
                identifier.bundesland,
            )

            if area not in valid_areas:
                raise RuntimeError(
                    f"Kein SNE-Tarifgebiet für "
                    f"{identifier.zpn_prefix} | "
                    f"{operator.name}: {area}"
                )

            areas_per_operator[operator.id].add(area)

            assignments.append(
                (
                    identifier,
                    operator,
                    area,
                )
            )

        conflicts = {
            operator_id: areas
            for operator_id, areas in areas_per_operator.items()
            if len(areas) > 1
        }

        if conflicts:
            raise RuntimeError(
                f"Ein Netzbetreiber wurde mehreren "
                f"SNE-Netzbereichen zugeordnet: {conflicts}"
            )

        counts = Counter(area for _, _, area in assignments)

        print("===== SNE NETWORK AREA IMPORT =====")
        print("Mode:", "APPLY" if args.apply else "DRY RUN")
        print("Strom identifiers:", len(assignments))

        print("\n===== COUNTS =====")
        for area, count in sorted(counts.items()):
            print(f"{area}: {count}")

        print("\n===== OVERRIDES =====")
        for identifier, operator, area in assignments:
            if area != identifier.bundesland:
                print(
                    f"{identifier.zpn_prefix} | "
                    f"{identifier.bundesland} -> {area} | "
                    f"{operator.name}"
                )

        if not args.apply:
            print("\nKeine Änderungen gespeichert.")
            print("Zum Speichern mit --apply ausführen.")
            return

        updated = 0
        unchanged = 0

        for _, operator, area in assignments:
            if operator.sne_network_area == area:
                unchanged += 1
                continue

            operator.sne_network_area = area
            updated += 1

        db.commit()

        print("\n===== RESULT =====")
        print("Updated:", updated)
        print("Unchanged:", unchanged)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
