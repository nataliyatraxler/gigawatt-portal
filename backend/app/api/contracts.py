from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.user import User, UserRole
from app.schemas.contract import (
    ContractCreate,
    ContractRead,
    ContractUpdate,
)
from app.services.contract import (
    create_contract_service,
    delete_contract_service,
    get_contract_service,
    get_contracts_by_agent_service,
    get_contracts_by_provider_service,
    get_contracts_service,
    update_contract_service,
)

router = APIRouter(
    prefix="/contracts",
    tags=["contracts"],
)


def check_contract_access(contract, current_user: User) -> None:
    if current_user.role == UserRole.SUPERADMIN:
        return

    if current_user.role == UserRole.AGENT:
        if contract.agent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this contract",
            )
        return

    if current_user.role == UserRole.LIEFERANT:
        if (
            current_user.provider_id is None
            or contract.provider_id != current_user.provider_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this contract",
            )
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )


@router.post(
    "",
    response_model=ContractRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_contract(
    contract_data: ContractCreate,
    agent_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.LIEFERANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lieferant cannot create contracts",
        )

    if current_user.role == UserRole.AGENT:
        effective_agent_id = current_user.id

    elif current_user.role == UserRole.SUPERADMIN:
        if agent_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="agent_id is required for superadmin",
            )

        agent = (
            db.query(User)
            .filter(
                User.id == agent_id,
                User.role == UserRole.AGENT,
            )
            .first()
        )

        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found",
            )

        effective_agent_id = agent_id

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return await create_contract_service(
        db,
        contract_data,
        effective_agent_id,
    )


@router.get(
    "",
    response_model=list[ContractRead],
)
async def list_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.SUPERADMIN:
        return await get_contracts_service(db)

    if current_user.role == UserRole.AGENT:
        return await get_contracts_by_agent_service(
            db,
            current_user.id,
        )

    if current_user.role == UserRole.LIEFERANT:
        if current_user.provider_id is None:
            return []

        return await get_contracts_by_provider_service(
            db,
            current_user.provider_id,
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )


@router.get(
    "/agent/{agent_id}",
    response_model=list[ContractRead],
)
async def list_contracts_by_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.SUPERADMIN:
        return await get_contracts_by_agent_service(
            db,
            agent_id,
        )

    if current_user.role == UserRole.AGENT:
        if agent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own contracts",
            )

        return await get_contracts_by_agent_service(
            db,
            current_user.id,
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )


@router.get(
    "/provider/{provider_id}",
    response_model=list[ContractRead],
)
async def list_contracts_by_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.SUPERADMIN:
        return await get_contracts_by_provider_service(
            db,
            provider_id,
        )

    if current_user.role == UserRole.LIEFERANT:
        if current_user.provider_id != provider_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view contracts for your provider",
            )

        return await get_contracts_by_provider_service(
            db,
            current_user.provider_id,
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )


@router.get(
    "/{contract_id}",
    response_model=ContractRead,
)
async def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = await get_contract_service(
        db,
        contract_id,
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    check_contract_access(
        contract,
        current_user,
    )

    return contract


@router.patch(
    "/{contract_id}",
    response_model=ContractRead,
)
async def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = await get_contract_service(
        db,
        contract_id,
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    check_contract_access(
        contract,
        current_user,
    )

    if current_user.role == UserRole.LIEFERANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lieferant cannot modify contracts",
        )

    return await update_contract_service(
        db,
        contract,
        contract_data,
    )


@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = await get_contract_service(
        db,
        contract_id,
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    check_contract_access(
        contract,
        current_user,
    )

    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can delete contracts",
        )

    await delete_contract_service(
        db,
        contract,
    )

    return None