from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.network_operator import NetworkOperator
from app.models.postal_code import PostalCode
from app.repositories.network import (
    get_all_network_operators,
    get_network_operator_by_id,
    get_network_operator_by_name,
    get_postal_codes,
    save_network_operator,
    save_postal_code,
)
from app.schemas.network import (
    NetworkOperatorCreate,
    NetworkOperatorUpdate,
    PostalCodeCreate,
)


def list_network_operators(
    db: Session,
) -> list[NetworkOperator]:
    return get_all_network_operators(db)


def find_network_operator(
    db: Session,
    operator_id: int,
) -> NetworkOperator:
    operator = get_network_operator_by_id(db, operator_id)

    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Netzbetreiber wurde nicht gefunden.",
        )

    return operator


def create_network_operator(
    db: Session,
    data: NetworkOperatorCreate,
) -> NetworkOperator:
    name = data.name.strip()

    if get_network_operator_by_name(db, name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ein Netzbetreiber mit diesem Namen existiert bereits.",
        )

    operator = NetworkOperator(
        name=name,
        code=data.code,
        active=True,
    )

    return save_network_operator(db, operator)


def update_network_operator(
    db: Session,
    operator_id: int,
    data: NetworkOperatorUpdate,
) -> NetworkOperator:
    operator = find_network_operator(db, operator_id)

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        name = update_data["name"].strip()

        existing = get_network_operator_by_name(db, name)

        if existing and existing.id != operator_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ein Netzbetreiber mit diesem Namen existiert bereits.",
            )

        operator.name = name

    for field in ("code", "active"):
        if field in update_data:
            setattr(operator, field, update_data[field])

    return save_network_operator(db, operator)


def create_postal_code(
    db: Session,
    data: PostalCodeCreate,
) -> PostalCode:
    operator = get_network_operator_by_id(
        db,
        data.network_operator_id,
    )

    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Netzbetreiber wurde nicht gefunden.",
        )

    postal_code = PostalCode(
        postal_code=data.postal_code.strip(),
        city=data.city.strip(),
        network_operator_id=data.network_operator_id,
    )

    return save_postal_code(db, postal_code)


def find_postal_codes(
    db: Session,
    postal_code: str,
) -> list[PostalCode]:
    results = get_postal_codes(
        db,
        postal_code.strip(),
    )

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Für diese Postleitzahl wurde kein Netzbetreiber gefunden.",
        )

    return results