from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


async def create_customer(
    db: Session,
    customer_data: CustomerCreate,
) -> Customer:
    customer = Customer(**customer_data.model_dump())

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


async def get_customer_by_id(
    db: Session,
    customer_id: int,
) -> Customer | None:
    return (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )


async def get_customers(
    db: Session,
) -> list[Customer]:
    return (
        db.query(Customer)
        .order_by(Customer.id)
        .all()
    )


async def update_customer(
    db: Session,
    customer: Customer,
    customer_data: CustomerUpdate,
) -> Customer:
    update_data = customer_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer


async def delete_customer(
    db: Session,
    customer: Customer,
) -> None:
    db.delete(customer)
    db.commit()