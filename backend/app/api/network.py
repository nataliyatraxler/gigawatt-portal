from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.auth import get_current_user
from app.dependencies.auth import require_superadmin
from app.models.user import User
from app.schemas.network import (
    NetworkOperatorCreate,
    NetworkOperatorResponse,
    NetworkOperatorUpdate,
    PostalCodeCreate,
    PostalCodeResponse,
)
from app.repositories.network import get_postal_code_by_id
from app.services.network_operator_resolver import (
    resolve_network_operator as resolve_network_operator_for_address,
)
from app.services.network import (
    create_network_operator,
    create_postal_code,
    find_network_operator,
    find_postal_codes,
    list_network_operators,
    update_network_operator,
    search_postal_codes_service,
    search_streets_service,
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
    "/network-operators/resolve-by-address",
    response_model=NetworkOperatorResponse | None,
)
def resolve_network_operator_by_address(
    postal_code_id: int,
    street_code: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    postal_code = get_postal_code_by_id(
        db,
        postal_code_id,
    )

    if not postal_code:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="PLZ/Ort wurde nicht gefunden.",
        )

    return resolve_network_operator_for_address(
        db,
        postal_code=postal_code,
        street_code=street_code,
    )


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
    "/postal-codes/search",
    response_model=list[PostalCodeResponse],
)
def search_postal_codes_endpoint(
    q: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return search_postal_codes_service(
        db,
        q,
    )

@router.get(
    "/postal-codes/{postal_code_id}/streets",
)
def search_streets_endpoint(
    postal_code_id: int,
    q: str = "",
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return search_streets_service(
        db,
        postal_code_id,
        q,
    )

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

from app.schemas.network import NetworkOperatorIdentifierResponse
from app.services.network import (
    list_network_operator_identifiers,
    resolve_network_operator_by_zpn,
)


@router.get(
    "/network-operator-identifiers",
    response_model=list[NetworkOperatorIdentifierResponse],
)
def get_network_operator_identifiers(
    energy_type: str,
    bundesland: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return list_network_operator_identifiers(
        db,
        energy_type,
        bundesland,
    )


@router.get(
    "/network-operator-identifiers/resolve",
    response_model=NetworkOperatorIdentifierResponse,
)
def resolve_network_operator(
    energy_type: str,
    zpn: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return resolve_network_operator_by_zpn(
        db,
        energy_type,
        zpn,
    )
