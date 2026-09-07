from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.tariff import Tariff
from app.repositories.provider import get_provider_by_id
from app.repositories.tariff import (
    get_all_tariffs,
    get_tariff_by_id,
    get_tariffs_by_provider,
    save_tariff,
)
from app.schemas.tariff import TariffCreate, TariffUpdate


def list_tariffs(
    db: Session,
    provider_id: int | None = None,
) -> list[Tariff]:
    if provider_id is not None:
        return get_tariffs_by_provider(db, provider_id)

    return get_all_tariffs(db)


def find_tariff(
    db: Session,
    tariff_id: int,
) -> Tariff:
    tariff = get_tariff_by_id(db, tariff_id)

    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarif wurde nicht gefunden.",
        )

    return tariff


def create_tariff(
    db: Session,
    tariff_data: TariffCreate,
) -> Tariff:
    provider = get_provider_by_id(
        db,
        tariff_data.provider_id,
    )

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lieferant wurde nicht gefunden.",
        )

    tariff = Tariff(
        **tariff_data.model_dump()
    )

    return save_tariff(db, tariff)


def update_tariff(
    db: Session,
    tariff_id: int,
    tariff_data: TariffUpdate,
) -> Tariff:
    tariff = find_tariff(db, tariff_id)

    update_data = tariff_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(tariff, field, value)

    return save_tariff(db, tariff)