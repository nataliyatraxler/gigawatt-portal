from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MonthlySettlementItem(Base):
    __tablename__ = "monthly_settlement_items"

    __table_args__ = (
        UniqueConstraint(
            "commission_entry_id",
            name="uq_monthly_settlement_item_commission",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    settlement_id: Mapped[int] = mapped_column(
        ForeignKey("monthly_settlements.id"),
        nullable=False,
        index=True,
    )

    commission_entry_id: Mapped[int] = mapped_column(
        ForeignKey("commission_entries.id"),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )