from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import require_superadmin
from app.models.user import User
from app.schemas.tariff import (
    TariffCreate,
    TariffResponse,
    TariffUpdate,
)
from app.services.tariff import (
    create_tariff,
    find_tariff,
    list_tariffs,
    update_tariff,
)


router = APIRouter(
    prefix="/tariffs",
    tags=["tariffs"],
)


@router.get(
    "",
    response_model=list[TariffResponse],
)
def get_tariffs(
    provider_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return list_tariffs(db, provider_id)


@router.get(
    "/{tariff_id}",
    response_model=TariffResponse,
)
def get_tariff(
    tariff_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return find_tariff(db, tariff_id)


@router.post(
    "",
    response_model=TariffResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_tariff(
    tariff_data: TariffCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return create_tariff(db, tariff_data)


@router.patch(
    "/{tariff_id}",
    response_model=TariffResponse,
)
def update_existing_tariff(
    tariff_id: int,
    tariff_data: TariffUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return update_tariff(db, tariff_id, tariff_data)