from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UsageFeeRule(Base):
    __tablename__ = "usage_fee_rules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # NULL = Regel gilt für das gesamte Netzgebiet
    # des Netzbetreibers.
    gkz: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
    )

    network_operator_id: Mapped[int] = mapped_column(
        ForeignKey(
            "network_operators.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    energy_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    calculation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    value: Mapped[Decimal] = mapped_column(
        Numeric(12, 6),
        nullable=False,
    )

    # NULL = keine Einschränkung auf einen konkreten Lieferanten.
    provider_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "providers.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # all / local_only
    supplier_scope: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="all",
        server_default="all",
    )

    include_metering_fee: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    valid_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    valid_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "gkz",
            "network_operator_id",
            "energy_type",
            "calculation_type",
            "provider_id",
            "supplier_scope",
            "valid_from",
            name="uq_usage_fee_rule",
        ),
    )
