from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Commission(Base):
    __tablename__ = "commissions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    tariff_id: Mapped[int] = mapped_column(
        ForeignKey("tariffs.id"),
        nullable=False,
        index=True,
    )

    supplier_commission: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    agent_commission: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    company_profit: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    valid_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    valid_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )