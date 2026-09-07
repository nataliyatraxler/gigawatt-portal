from sqlalchemy.orm import Session

from app.models.tariff_network_operator import TariffNetworkOperator


def get_link(
    db: Session,
    tariff_id: int,
    network_operator_id: int,
) -> TariffNetworkOperator | None:
    return (
        db.query(TariffNetworkOperator)
        .filter(
            TariffNetworkOperator.tariff_id == tariff_id,
            TariffNetworkOperator.network_operator_id == network_operator_id,
        )
        .first()
    )


def get_links_by_tariff(
    db: Session,
    tariff_id: int,
) -> list[TariffNetworkOperator]:
    return (
        db.query(TariffNetworkOperator)
        .filter(TariffNetworkOperator.tariff_id == tariff_id)
        .order_by(TariffNetworkOperator.network_operator_id)
        .all()
    )


def create_link(
    db: Session,
    tariff_id: int,
    network_operator_id: int,
) -> TariffNetworkOperator:
    link = TariffNetworkOperator(
        tariff_id=tariff_id,
        network_operator_id=network_operator_id,
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


def delete_link(
    db: Session,
    link: TariffNetworkOperator,
) -> None:
    db.delete(link)
    db.commit()