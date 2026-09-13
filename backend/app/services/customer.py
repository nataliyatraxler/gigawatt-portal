from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.repositories.customer import (
    create_customer,
    delete_customer,
    get_customer_by_id,
    get_customers,
    update_customer,
)
from app.schemas.customer import CustomerCreate, CustomerUpdate


async def create_customer_service(
    db: AsyncSession,
    customer_data: CustomerCreate,
) -> Customer:
    return await create_customer(db, customer_data)


async def get_customer_service(
    db: AsyncSession,
    customer_id: int,
) -> Customer | None:
    return await get_customer_by_id(db, customer_id)


async def get_customers_service(
    db: AsyncSession,
) -> list[Customer]:
    return await get_customers(db)


async def update_customer_service(
    db: AsyncSession,
    customer: Customer,
    customer_data: CustomerUpdate,
) -> Customer:
    return await update_customer(db, customer, customer_data)


async def delete_customer_service(
    db: AsyncSession,
    customer: Customer,
) -> None:
    await delete_customer(db, customer)