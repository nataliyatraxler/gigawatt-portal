from sqlalchemy import or_
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

def get_postal_code_by_id(
    db: Session,
    postal_code_id: int,
) -> PostalCode | None:
    return (
        db.query(PostalCode)
        .filter(PostalCode.id == postal_code_id)
        .first()
    )

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

def get_network_operators_for_postal_code(
    db: Session,
    postal_code: str,
) -> list["NetworkOperator"]:
    postal_codes = get_postal_codes(
        db,
        postal_code,
    )

    operator_ids = {
        row.network_operator_id
        for row in postal_codes
        if row.network_operator_id is not None
    }

    if not operator_ids:
        return []

    return (
        db.query(NetworkOperator)
        .filter(NetworkOperator.id.in_(operator_ids))
        .order_by(NetworkOperator.name)
        .all()
    )

def search_postal_codes(
    db: Session,
    query: str,
    limit: int = 20,
) -> list[PostalCode]:
    search = query.strip()

    if not search:
        return []

    return (
        db.query(PostalCode)
        .filter(
            or_(
                PostalCode.postal_code.ilike(f"{search}%"),
                PostalCode.city.ilike(f"%{search}%"),
            )
        )
        .order_by(
            PostalCode.postal_code,
            PostalCode.city,
        )
        .limit(limit)
        .all()
    )

def get_network_operator_identifiers(
    db: Session,
    energy_type: str,
    bundesland: str | None = None,
):
    from app.models.network_operator_identifier import (
        NetworkOperatorIdentifier,
    )
    from app.models.network_operator_dropdown_mapping import (
        NetworkOperatorDropdownMapping,
    )

    # Strom dropdown logic comes from the customer-provided
    # Dropdown_Mapping table. This is intentionally separate
    # from NetworkOperatorIdentifier.bundesland because one
    # operator can be shown in several Bundesländer.
    if energy_type == "Strom" and bundesland:
        return (
            db.query(
                NetworkOperatorIdentifier,
                NetworkOperator,
                NetworkOperatorDropdownMapping,
            )
            .join(
                NetworkOperator,
                NetworkOperator.id
                == NetworkOperatorIdentifier.network_operator_id,
            )
            .join(
                NetworkOperatorDropdownMapping,
                NetworkOperatorDropdownMapping.network_operator_identifier_id
                == NetworkOperatorIdentifier.id,
            )
            .filter(
                NetworkOperatorIdentifier.energy_type == energy_type,
                NetworkOperatorIdentifier.active.is_(True),
                NetworkOperator.active.is_(True),
                NetworkOperatorDropdownMapping.bundesland == bundesland,
            )
            .order_by(
                NetworkOperatorDropdownMapping.priority,
                NetworkOperator.name,
            )
            .all()
        )

    # Existing behaviour remains unchanged for:
    # - Strom without Bundesland
    # - Gas
    query = (
        db.query(
            NetworkOperatorIdentifier,
            NetworkOperator,
        )
        .join(
            NetworkOperator,
            NetworkOperator.id
            == NetworkOperatorIdentifier.network_operator_id,
        )
        .filter(
            NetworkOperatorIdentifier.energy_type == energy_type,
            NetworkOperatorIdentifier.active.is_(True),
            NetworkOperator.active.is_(True),
        )
    )

    if bundesland:
        query = query.filter(
            NetworkOperatorIdentifier.bundesland == bundesland
        )

    return (
        query
        .order_by(NetworkOperator.name)
        .all()
    )


def get_network_operator_by_zpn_prefix(
    db: Session,
    energy_type: str,
    zpn_prefix: str,
):
    from app.models.network_operator_identifier import (
        NetworkOperatorIdentifier,
    )

    return (
        db.query(
            NetworkOperatorIdentifier,
            NetworkOperator,
        )
        .join(
            NetworkOperator,
            NetworkOperator.id
            == NetworkOperatorIdentifier.network_operator_id,
        )
        .filter(
            NetworkOperatorIdentifier.energy_type == energy_type,
            NetworkOperatorIdentifier.zpn_prefix == zpn_prefix,
            NetworkOperatorIdentifier.active.is_(True),
            NetworkOperator.active.is_(True),
        )
        .first()
    )
