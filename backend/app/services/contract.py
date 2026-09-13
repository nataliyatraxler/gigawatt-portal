from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.repositories.contract import (
    create_contract,
    delete_contract,
    get_contract_by_id,
    get_contracts,
    get_contracts_by_agent,
    get_contracts_by_provider,
    update_contract,
)
from app.schemas.contract import ContractCreate, ContractUpdate


async def create_contract_service(
    db: Session,
    contract_data: ContractCreate,
    agent_id: int,
) -> Contract:
    return await create_contract(
        db,
        contract_data,
        agent_id,
    )


async def get_contract_service(
    db: Session,
    contract_id: int,
) -> Contract | None:
    return await get_contract_by_id(
        db,
        contract_id,
    )


async def get_contracts_service(
    db: Session,
) -> list[Contract]:
    return await get_contracts(db)


async def get_contracts_by_agent_service(
    db: Session,
    agent_id: int,
) -> list[Contract]:
    return await get_contracts_by_agent(
        db,
        agent_id,
    )


async def get_contracts_by_provider_service(
    db: Session,
    provider_id: int,
) -> list[Contract]:
    return await get_contracts_by_provider(
        db,
        provider_id,
    )


async def update_contract_service(
    db: Session,
    contract: Contract,
    contract_data: ContractUpdate,
) -> Contract:
    return await update_contract(
        db,
        contract,
        contract_data,
    )


async def delete_contract_service(
    db: Session,
    contract: Contract,
) -> None:
    await delete_contract(
        db,
        contract,
    )