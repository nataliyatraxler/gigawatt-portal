from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class RegulatoryCharge(Base):
    __tablename__ = "regulatory_charges"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
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

    network_level: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    tariff_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    network_area: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    customer_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    valid_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    valid_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            "calculation_type",
            "network_level",
            "tariff_type",
            "network_area",
            "customer_type",
            "valid_from",
            name="uq_regulatory_charge",
        ),
    )
