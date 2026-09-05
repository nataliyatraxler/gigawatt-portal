from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    contract_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    agent_id: Mapped[int] = mapped_column(
    ForeignKey("users.id"),
    nullable=False,
    index=True,
    )
    
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("providers.id"),
        nullable=False,
        index=True,
    )

    tariff_id: Mapped[int] = mapped_column(
        ForeignKey("tariffs.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
    )

    annual_consumption: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    supplier_commission: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    agent_commission: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    company_profit: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    signed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    cancelled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )