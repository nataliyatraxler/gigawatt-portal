from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.network import get_network_operator_by_id
from app.repositories.tariff import get_tariff_by_id
from app.repositories.tariff_network import (
    create_link,
    delete_link,
    get_link,
    get_links_by_tariff,
)


def list_tariff_networks(
    db: Session,
    tariff_id: int,
):
    tariff = get_tariff_by_id(db, tariff_id)

    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarif wurde nicht gefunden.",
        )

    return get_links_by_tariff(db, tariff_id)


def add_tariff_network(
    db: Session,
    tariff_id: int,
    network_operator_id: int,
):
    tariff = get_tariff_by_id(db, tariff_id)

    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarif wurde nicht gefunden.",
        )

    operator = get_network_operator_by_id(
        db,
        network_operator_id,
    )

    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Netzbetreiber wurde nicht gefunden.",
        )

    existing = get_link(
        db,
        tariff_id,
        network_operator_id,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Der Tarif ist diesem Netzbetreiber bereits zugeordnet.",
        )

    return create_link(
        db,
        tariff_id,
        network_operator_id,
    )


def remove_tariff_network(
    db: Session,
    tariff_id: int,
    network_operator_id: int,
) -> None:
    link = get_link(
        db,
        tariff_id,
        network_operator_id,
    )

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diese Tarif-Netzbetreiber-Zuordnung wurde nicht gefunden.",
        )

    delete_link(db, link)