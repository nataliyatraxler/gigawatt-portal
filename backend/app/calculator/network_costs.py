from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.network_metering_fee import NetworkMeteringFee
from app.models.sne_tariff import SneTariff


CENT = Decimal("100")
MONEY = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def calculate_sne_network_costs(
    db: Session,
    *,
    year: int,
    network_area: str,
    network_operator_id: int,
    network_level: int,
    tariff_type: str,
    consumption_kwh: Decimal,
    meter_type: str = "standard",
) -> dict:
    tariff = (
        db.query(SneTariff)
        .filter(
            SneTariff.year == year,
            SneTariff.network_area == network_area,
            SneTariff.network_level == network_level,
            SneTariff.tariff_type == tariff_type,
        )
        .one_or_none()
    )

    if tariff is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Für den Netzbereich '{network_area}' ist kein "
                f"SNE-Tarif für {year}, Netzebene {network_level} "
                f"und Tariftyp '{tariff_type}' hinterlegt."
            ),
        )

    metering_fee = (
        db.query(NetworkMeteringFee)
        .filter(
            NetworkMeteringFee.network_operator_id == network_operator_id,
            NetworkMeteringFee.year == year,
            NetworkMeteringFee.meter_type == meter_type,
        )
        .one_or_none()
    )

    if metering_fee is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Für den Netzbetreiber ist kein Messentgelt "
                f"für {year} und Zählertyp '{meter_type}' hinterlegt."
            ),
        )

    lp_cent = tariff.lp_cent or Decimal("0")
    ap_cent_kwh = tariff.ap_cent_kwh or Decimal("0")
    network_loss_cent_kwh = (
        tariff.network_loss_cent_kwh or Decimal("0")
    )

    # NE7 nicht gemessen:
    # LP is an annual fixed amount in cent.
    base_price = lp_cent / CENT

    work_price = (
        consumption_kwh * ap_cent_kwh / CENT
    )

    network_loss = (
        consumption_kwh * network_loss_cent_kwh / CENT
    )

    metering_cost = metering_fee.annual_fee

    total = (
        base_price
        + work_price
        + network_loss
        + metering_cost
    )

    return {
        "year": year,
        "network_area": network_area,
        "network_operator_id": network_operator_id,
        "network_level": network_level,
        "tariff_type": tariff_type,
        "consumption_kwh": consumption_kwh,
        "base_price": money(base_price),
        "work_price": money(work_price),
        "network_loss": money(network_loss),
        "metering_cost": money(metering_cost),
        "total_network_tariff": money(total),
    }
