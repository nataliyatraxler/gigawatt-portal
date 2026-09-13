from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerRead,
    CustomerUpdate,
)
from app.services.customer import (
    create_customer_service,
    delete_customer_service,
    get_customer_service,
    get_customers_service,
    update_customer_service,
)

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)


@router.post(
    "",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_customer_service(db, customer_data)


@router.get(
    "",
    response_model=list[CustomerRead],
)
async def list_customers(
    db: AsyncSession = Depends(get_db),
):
    return await get_customers_service(db)


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
):
    customer = await get_customer_service(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


@router.patch(
    "/{customer_id}",
    response_model=CustomerRead,
)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
):
    customer = await get_customer_service(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return await update_customer_service(
        db,
        customer,
        customer_data,
    )


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
):
    customer = await get_customer_service(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    await delete_customer_service(db, customer)

    return None