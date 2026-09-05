from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CommissionEntry(Base):
    __tablename__ = "commission_entries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id"),
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

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    source_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )