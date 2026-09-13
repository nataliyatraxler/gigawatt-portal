from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.schemas.contract import ContractCreate, ContractUpdate


async def create_contract(
    db: Session,
    contract_data: ContractCreate,
    agent_id: int,
) -> Contract:
    contract = Contract(
        **contract_data.model_dump(),
        agent_id=agent_id,
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return contract


async def get_contract_by_id(
    db: Session,
    contract_id: int,
) -> Contract | None:
    return (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )


async def get_contracts(
    db: Session,
) -> list[Contract]:
    return (
        db.query(Contract)
        .order_by(Contract.id)
        .all()
    )


async def get_contracts_by_agent(
    db: Session,
    agent_id: int,
) -> list[Contract]:
    return (
        db.query(Contract)
        .filter(Contract.agent_id == agent_id)
        .order_by(Contract.id)
        .all()
    )


async def get_contracts_by_provider(
    db: Session,
    provider_id: int,
) -> list[Contract]:
    return (
        db.query(Contract)
        .filter(Contract.provider_id == provider_id)
        .order_by(Contract.id)
        .all()
    )


async def update_contract(
    db: Session,
    contract: Contract,
    contract_data: ContractUpdate,
) -> Contract:
    update_data = contract_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(contract, field, value)

    db.commit()
    db.refresh(contract)

    return contract


async def delete_contract(
    db: Session,
    contract: Contract,
) -> None:
    db.delete(contract)
    db.commit()