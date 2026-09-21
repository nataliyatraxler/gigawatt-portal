from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import csv
from pathlib import Path
from app.models.network_operator import NetworkOperator
from app.models.postal_code import PostalCode
from app.repositories.network import (
    get_all_network_operators,
    get_network_operator_by_id,
    get_network_operator_by_name,
    get_postal_codes,
    search_postal_codes,
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
def search_postal_codes_service(
    db: Session,
    query: str,
) -> list[PostalCode]:
    return search_postal_codes(
        db,
        query,
    )

BEV_DATA_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "Adresse_Relationale_Tabellen_Stichtagsdaten"
)


def search_streets_service(
    db: Session,
    postal_code_id: int,
    query: str = "",
) -> list[dict]:
    postal_code = (
        db.query(PostalCode)
        .filter(PostalCode.id == postal_code_id)
        .first()
    )

    if not postal_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postleitzahl/Ort wurde nicht gefunden.",
        )

    locality_file = BEV_DATA_DIR / "ORTSCHAFT.csv"
    address_file = BEV_DATA_DIR / "ADRESSE.csv"
    street_file = BEV_DATA_DIR / "STRASSE.csv"

    locality_keys = set()

    with open(
        locality_file,
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            if (
                row["GKZ"] == postal_code.gkz
                and row["ORTSNAME"] == postal_code.city
            ):
                locality_keys.add(
                    (row["GKZ"], row["OKZ"])
                )

    street_codes = set()

    with open(
        address_file,
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            if (
                row["PLZ"] == postal_code.postal_code
                and (row["GKZ"], row["OKZ"]) in locality_keys
            ):
                street_codes.add(row["SKZ"])

    search = query.strip().lower()
    streets = []

    with open(
        street_file,
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            name = row["STRASSENNAME"]

            if (
                row["SKZ"] in street_codes
                and (
                    not search
                    or search in name.lower()
                )
            ):
                streets.append(
                    {
                        "street_code": row["SKZ"],
                        "name": name,
                    }
                )

    streets.sort(
        key=lambda item: item["name"].lower()
    )

    return streets[:30]