from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import require_superadmin
from app.models.user import User
from app.schemas.network import (
    NetworkOperatorCreate,
    NetworkOperatorResponse,
    NetworkOperatorUpdate,
    PostalCodeCreate,
    PostalCodeResponse,
)
from app.services.network import (
    create_network_operator,
    create_postal_code,
    find_network_operator,
    find_postal_codes,
    list_network_operators,
    update_network_operator,
)


router = APIRouter(
    tags=["network"],
)


@router.get(
    "/network-operators",
    response_model=list[NetworkOperatorResponse],
)
def get_network_operators(
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return list_network_operators(db)


@router.get(
    "/network-operators/{operator_id}",
    response_model=NetworkOperatorResponse,
)
def get_network_operator(
    operator_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return find_network_operator(db, operator_id)


@router.post(
    "/network-operators",
    response_model=NetworkOperatorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_network_operator(
    data: NetworkOperatorCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return create_network_operator(db, data)


@router.patch(
    "/network-operators/{operator_id}",
    response_model=NetworkOperatorResponse,
)
def update_existing_network_operator(
    operator_id: int,
    data: NetworkOperatorUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return update_network_operator(db, operator_id, data)


@router.post(
    "/postal-codes",
    response_model=PostalCodeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_postal_code(
    data: PostalCodeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return create_postal_code(db, data)


@router.get(
    "/postal-codes/{postal_code}",
    response_model=list[PostalCodeResponse],
)
def get_postal_code(
    postal_code: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return find_postal_codes(db, postal_code)