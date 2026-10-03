from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.gas_network_tariff import GasNetworkTariff
from app.models.network_operator import NetworkOperator
from app.models.network_operator_identifier import NetworkOperatorIdentifier


def resolve_gas_network_area(
    db: Session,
    *,
    network_operator_id: int,
) -> str:
    operator = (
        db.query(NetworkOperator)
        .filter(NetworkOperator.id == network_operator_id)
        .first()
    )

    if operator is None:
        raise HTTPException(
            status_code=404,
            detail="Netzbetreiber nicht gefunden.",
        )

    identifier = (
        db.query(NetworkOperatorIdentifier)
        .filter(
            NetworkOperatorIdentifier.network_operator_id
            == network_operator_id,
            NetworkOperatorIdentifier.energy_type == "Gas",
            NetworkOperatorIdentifier.active.is_(True),
        )
        .first()
    )

    if identifier is None:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Für den Netzbetreiber '{operator.name}' "
                "ist keine aktive Gas-ZPN-Kennung hinterlegt."
            ),
        )

    if not identifier.bundesland:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Für den Gas-Netzbetreiber '{operator.name}' "
                "ist kein Netzbereich/Bundesland hinterlegt."
            ),
        )

    return identifier.bundesland



def convert_gas_m3_to_kwh(
    *,
    consumption_m3: Decimal,
    conversion_factor_kwh_m3: Decimal,
) -> Decimal:
    if consumption_m3 <= 0:
        raise HTTPException(
            status_code=422,
            detail="Gasverbrauch in m³ muss größer als 0 sein.",
        )

    if conversion_factor_kwh_m3 <= 0:
        raise HTTPException(
            status_code=422,
            detail="Gas-Umrechnungsfaktor muss größer als 0 sein.",
        )

    return consumption_m3 * conversion_factor_kwh_m3


def get_gas_network_tariffs(
    db: Session,
    *,
    network_operator_id: int,
    year: int,
    network_level: int,
    tariff_variant: str,
) -> list[GasNetworkTariff]:
    network_area = resolve_gas_network_area(
        db,
        network_operator_id=network_operator_id,
    )

    tariffs = (
        db.query(GasNetworkTariff)
        .filter(
            GasNetworkTariff.year == year,
            GasNetworkTariff.network_area == network_area,
            GasNetworkTariff.network_level == network_level,
            GasNetworkTariff.tariff_variant == tariff_variant,
        )
        .order_by(GasNetworkTariff.consumption_from_kwh.asc())
        .all()
    )

    if not tariffs:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Keine Gas-Netzentgelte für {network_area}, "
                f"Netzebene {network_level}, Jahr {year}, "
                f"Variante '{tariff_variant}' gefunden."
            ),
        )

    return tariffs

def select_gas_network_tariff(
    tariffs: list[GasNetworkTariff],
    *,
    consumption_kwh: Decimal,
) -> GasNetworkTariff:
    for tariff in tariffs:
        lower = tariff.consumption_from_kwh
        upper = tariff.consumption_to_kwh

        if consumption_kwh < lower:
            continue

        if upper is None or consumption_kwh <= upper:
            return tariff

    raise HTTPException(
        status_code=422,
        detail=(
            "Für den Gasverbrauch "
            f"{consumption_kwh} kWh wurde keine Verbrauchsstaffel gefunden."
        ),
    )


def calculate_gas_arbeitspreis(
    tariffs: list[GasNetworkTariff],
    *,
    consumption_kwh: Decimal,
) -> Decimal:
    if consumption_kwh <= 0:
        raise HTTPException(
            status_code=422,
            detail="Gasverbrauch in kWh muss größer als 0 sein.",
        )

    if not tariffs:
        raise HTTPException(
            status_code=422,
            detail="Keine Gas-Tarifzonen vorhanden.",
        )

    total_cent = Decimal("0")
    covered_until = Decimal("0")

    for tariff in sorted(
        tariffs,
        key=lambda item: item.consumption_from_kwh,
    ):
        lower = tariff.consumption_from_kwh
        upper = tariff.consumption_to_kwh
        price = tariff.arbeitspreis_cent_kwh

        if price is None:
            continue

        if consumption_kwh <= lower:
            break

        band_end = consumption_kwh

        if upper is not None:
            band_end = min(consumption_kwh, upper)

        band_consumption = band_end - lower

        if band_consumption <= 0:
            continue

        total_cent += band_consumption * price
        covered_until = max(covered_until, band_end)

        if upper is None or consumption_kwh <= upper:
            break

    if covered_until < consumption_kwh:
        raise HTTPException(
            status_code=422,
            detail=(
                "Die Gas-Tarifzonen decken den Jahresverbrauch "
                f"von {consumption_kwh} kWh nicht vollständig ab."
            ),
        )

    return total_cent / Decimal("100")


def calculate_gas_network_usage_costs(
    db: Session,
    *,
    year: int,
    network_operator_id: int,
    consumption_kwh: Decimal,
    network_level: int = 3,
) -> dict:
    tariff_variant = "nicht_leistungsgemessen"

    if network_level != 3:
        raise HTTPException(
            status_code=422,
            detail=(
                "Nicht leistungsgemessene Gas-Anlagen werden derzeit "
                "nur für Netzebene 3 berechnet."
            ),
        )

    tariffs = get_gas_network_tariffs(
        db,
        network_operator_id=network_operator_id,
        year=year,
        network_level=network_level,
        tariff_variant=tariff_variant,
    )

    work_price = calculate_gas_arbeitspreis(
        tariffs,
        consumption_kwh=consumption_kwh,
    )

    selected_tariff = select_gas_network_tariff(
        tariffs,
        consumption_kwh=consumption_kwh,
    )

    pauschale_cent = (
        selected_tariff.pauschale_cent_year
        or Decimal("0")
    )

    base_price = pauschale_cent / Decimal("100")
    subtotal = base_price + work_price

    return {
        "year": year,
        "network_area": selected_tariff.network_area,
        "network_operator_id": network_operator_id,
        "network_level": network_level,
        "tariff_type": tariff_variant,
        "consumption_kwh": consumption_kwh,
        "base_price": base_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "work_price": work_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "network_usage_subtotal": subtotal.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        ),
    }
