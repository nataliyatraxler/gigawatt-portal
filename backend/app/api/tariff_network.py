from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import require_superadmin
from app.models.user import User
from app.schemas.tariff_network import TariffNetworkResponse
from app.services.tariff_network import (
    add_tariff_network,
    list_tariff_networks,
    remove_tariff_network,
)


router = APIRouter(
    tags=["tariff-networks"],
)


@router.get(
    "/tariffs/{tariff_id}/network-operators",
    response_model=list[TariffNetworkResponse],
)
def get_tariff_networks(
    tariff_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return list_tariff_networks(db, tariff_id)


@router.post(
    "/tariffs/{tariff_id}/network-operators/{operator_id}",
    response_model=TariffNetworkResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_network_operator_to_tariff(
    tariff_id: int,
    operator_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return add_tariff_network(
        db,
        tariff_id,
        operator_id,
    )


@router.delete(
    "/tariffs/{tariff_id}/network-operators/{operator_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_network_operator_from_tariff(
    tariff_id: int,
    operator_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    remove_tariff_network(
        db,
        tariff_id,
        operator_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)