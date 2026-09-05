from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MonthlySettlement(Base):
    __tablename__ = "monthly_settlements"

    __table_args__ = (
        UniqueConstraint(
            "agent_id",
            "year",
            "month",
            name="uq_monthly_settlement_agent_period",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )