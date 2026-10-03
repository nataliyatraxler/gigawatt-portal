from datetime import date
from decimal import Decimal

from app.database.session import SessionLocal
from app.models.network_operator import NetworkOperator
from app.models.postal_code import PostalCode
from app.models.usage_fee_rule import UsageFeeRule


VALID_FROM = date(2026, 8, 14)
SOURCE = "E-Control Gebrauchsabgabe Version 15.0 / 14.08.2026"


RULES = [
    {
        "operator": "Elektrizitätswerk Bad Hofgastein Gesellschaft m.b.H.",
        "gkz": "50402",
        "type": "cent_per_kwh",
        "value": "0.4893",
    },
    {
        "operator": "Elektrizitätswerk der Gemeinde Gries am Brenner",
        "gkz": "70313",
        "type": "percent_of_energy_and_network",
        "value": "6",
    },
    {
        "operator": "Elektrizitätswerke Reutte AG",
        "gkz": "70828",
        "type": "percent_of_energy_cost",
        "value": "6",
    },
    {
        "operator": "Energie Klagenfurt GmbH",
        "gkz": "20101",
        "type": "cent_per_kwh",
        "value": "1.637",
    },
    {
        "operator": "Energie Ried GmbH",
        "gkz": "41225",
        "type": "percent_of_energy_cost",
        "value": "3",
        "supplier_scope": "local_only",
    },
    {
        "operator": "EWA Energie- und Wirtschaftsbetriebe der Gemeinde St. Anton GmbH",
        "gkz": "70621",
        "type": "percent_of_energy_and_network",
        "value": "6",
    },
    {
        "operator": "Gemeinde Kematen",
        "gkz": "70320",
        "type": "percent_of_energy_and_network",
        "value": "6",
    },
    {
        "operator": "HALLAG Kommunal GmbH",
        "gkz": "70354",
        "type": "percent_of_energy_and_network",
        "value": "6",
    },
    {
        "operator": "Innsbrucker Kommunalbetriebe AG",
        "gkz": "70101",
        "type": "percent_of_energy_cost",
        "value": "6",
    },
    {
        "operator": "Kommunalbetriebe Hopfgarten GmbH",
        "gkz": "70406",
        "type": "percent_of_energy_and_network",
        "value": "6",
    },
    {
        "operator": "Kommunalbetriebe Rinn GmbH",
        "gkz": "70345",
        "type": "percent_of_energy_and_network",
        "value": "6",
    },
    {
        "operator": "Licht- und Kraftstromvertrieb der Marktgemeinde Göstling an der Ybbs",
        "gkz": "32002",
        "type": "cent_per_kwh",
        "value": "0.1013",
    },
    {
        "operator": "Licht- und Kraftvertrieb der Gemeinde Hollenstein an der Ybbs",
        "gkz": "30516",
        "type": "cent_per_kwh",
        "value": "0.1013",
    },
    {
        "operator": "Marktgemeinde Neumarkt Versorgungsbetriebsges.m.b.H.",
        "gkz": "61439",
        "type": "percent_of_network_tariff",
        "value": "3",
    },
    {
        "operator": "Murauer Stadtwerke Gesellschaft m.b.H.",
        "gkz": "61438",
        "type": "percent_of_network_tariff",
        "value": "3",
    },
    {
        "operator": "Polsterer Kerres Ruttin Holding GmbH",
        "gkz": "30733",
        "type": "cent_per_kwh",
        "value": "0.1059",
    },

    # Salzburg Netz: Regel gilt für das gesamte Netzgebiet.
    {
        "operator": "Salzburg Netz GmbH",
        "gkz": None,
        "type": "cent_per_kwh",
        "value": "0.3789",
    },

    {
        "operator": "Stadtbetriebe Mariazell Ges.m.b.H.",
        "gkz": "62142",
        "type": "percent_of_network_tariff",
        "value": "3",
    },
    {
        "operator": "Städtische Betriebe Rottenmann GmbH",
        "gkz": "61263",
        "type": "percent_of_energy_and_network",
        "value": "3",
        "supplier_scope": "local_only",
    },
    {
        "operator": "Stadtwerke Bruck an der Mur GmbH",
        "gkz": "62139",
        "type": "percent_of_network_tariff",
        "value": "3",
        "include_metering_fee": False,
    },
    {
        "operator": 'Stadtgemeinde Imst, Inhaberin der nicht prot. Fa. "Stadtwerke Imst"',
        "gkz": "70203",
        "type": "percent_of_network_tariff",
        "value": "6",
    },
    {
        "operator": "Stadtwerke Judenburg AG",
        "gkz": "62040",
        "type": "percent_of_network_tariff",
        "value": "3",
    },
    {
        "operator": "Stadtwerke Kitzbühel",
        "gkz": "70411",
        "type": "percent_of_energy_and_network",
        "value": "6",
    },
    {
        "operator": "Stadtwerke Kufstein GmbH",
        "gkz": "70513",
        "type": "percent_of_energy_and_network",
        "value": "6",
    },
    {
        "operator": "Stadtwerke Mürzzuschlag Ges.m.b.H.",
        "gkz": "62143",
        "type": "percent_of_energy_and_network",
        "value": "3",
        "supplier_scope": "local_only",
        "include_metering_fee": False,
    },
    {
        "operator": "Stadtwerke Schwaz GmbH",
        "gkz": "70926",
        "type": "percent_of_energy_and_network",
        "value": "6",
    },
    {
        "operator": "Stadtwerke Trofaiach Gesellschaft m.b.H.",
        "gkz": "61120",
        "type": "percent_of_network_tariff",
        "value": "3",
        "include_metering_fee": False,
    },
    {
        "operator": "Stadtwerke Wörgl GmbH",
        "gkz": "70531",
        "type": "percent_of_energy_and_network",
        "value": "6",
    },
    {
        "operator": "Wiener Netze",
        "gkz": "90001",
        "type": "percent_of_energy_and_network",
        "value": "7",
    },
]


def main() -> None:
    db = SessionLocal()

    try:
        print(f"Regeln: {len(RULES)}")
        print(f"Gültig ab: {VALID_FROM}")
        print()

        errors = []

        for index, rule in enumerate(RULES, start=1):
            operator = (
                db.query(NetworkOperator)
                .filter(NetworkOperator.name == rule["operator"])
                .one_or_none()
            )

            if operator is None:
                errors.append(
                    f"{index}: Netzbetreiber fehlt: {rule['operator']}"
                )
                print(
                    f"ERROR {index:02d} | Netzbetreiber nicht gefunden | "
                    f"{rule['operator']}"
                )
                continue

            gkz = rule["gkz"]

            if gkz is not None:
                municipality = (
                    db.query(PostalCode.municipality)
                    .filter(PostalCode.gkz == gkz)
                    .first()
                )

                if municipality is None:
                    errors.append(
                        f"{index}: GKZ fehlt: {gkz}"
                    )
                    print(
                        f"ERROR {index:02d} | GKZ {gkz} nicht gefunden"
                    )
                    continue

                municipality_name = municipality[0]
            else:
                municipality_name = "gesamtes Netzgebiet"

            supplier_scope = rule.get(
                "supplier_scope",
                "all",
            )

            include_metering_fee = rule.get(
                "include_metering_fee",
                True,
            )

            print(
                f"OK {index:02d} | "
                f"NB {operator.id:>3} | "
                f"GKZ {str(gkz):>5} | "
                f"{municipality_name:<28} | "
                f"{rule['type']:<30} | "
                f"{rule['value']:>7} | "
                f"{supplier_scope:<10} | "
                f"Messentgelt={include_metering_fee}"
            )

        print()
        if errors:
            print(f"FEHLER: {len(errors)}")
            for error in errors:
                print(" -", error)
            raise SystemExit(1)

        print("DRY-RUN OK")
        print("Keine Daten wurden gespeichert.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
