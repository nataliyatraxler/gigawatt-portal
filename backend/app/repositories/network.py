from sqlalchemy.orm import Session

from app.models.network_operator import NetworkOperator
from app.models.postal_code import PostalCode


def get_all_network_operators(
    db: Session,
) -> list[NetworkOperator]:
    return (
        db.query(NetworkOperator)
        .order_by(NetworkOperator.name)
        .all()
    )


def get_network_operator_by_id(
    db: Session,
    operator_id: int,
) -> NetworkOperator | None:
    return (
        db.query(NetworkOperator)
        .filter(NetworkOperator.id == operator_id)
        .first()
    )


def get_network_operator_by_name(
    db: Session,
    name: str,
) -> NetworkOperator | None:
    return (
        db.query(NetworkOperator)
        .filter(NetworkOperator.name == name)
        .first()
    )


def save_network_operator(
    db: Session,
    operator: NetworkOperator,
) -> NetworkOperator:
    db.add(operator)
    db.commit()
    db.refresh(operator)

    return operator


def save_postal_code(
    db: Session,
    postal_code: PostalCode,
) -> PostalCode:
    db.add(postal_code)
    db.commit()
    db.refresh(postal_code)

    return postal_code


def get_postal_codes(
    db: Session,
    postal_code: str,
) -> list[PostalCode]:
    return (
        db.query(PostalCode)
        .filter(PostalCode.postal_code == postal_code)
        .order_by(PostalCode.city)
        .all()
    )