from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class NetworkMeteringFee(Base):
    __tablename__ = "network_metering_fees"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    network_operator_id: Mapped[int] = mapped_column(
        ForeignKey("network_operators.id"),
        nullable=False,
        index=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    energy_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    meter_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    annual_fee: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    network_operator = relationship(
        "NetworkOperator",
        back_populates="metering_fees",
    )

    __table_args__ = (
        UniqueConstraint(
            "network_operator_id",
            "year",
            "energy_type",
            "meter_type",
            name="uq_network_metering_fee",
        ),
    )
