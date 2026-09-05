from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ContractStatus(str, Enum):
    DRAFT = "draft"
    SIGNED = "signed"
    SUBMITTED_TO_SUPPLIER = "submitted_to_supplier"
    ACCEPTED_BY_SUPPLIER = "accepted_by_supplier"
    ACTIVATED = "activated"
    COMMISSION_CONFIRMED = "commission_confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ContractStatusHistory(Base):
    __tablename__ = "contract_status_history"

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

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    changed_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )