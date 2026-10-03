from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class GasNetworkTariff(Base):
    __tablename__ = "gas_network_tariffs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    network_area: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    network_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    tariff_variant: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    consumption_from_kwh: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        nullable=False,
    )

    consumption_to_kwh: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 3),
        nullable=True,
    )

    arbeitspreis_cent_kwh: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    leistungspreis_cent_kwh_h: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    pauschale_cent_year: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "year",
            "network_area",
            "network_level",
            "tariff_variant",
            "consumption_from_kwh",
            name="uq_gas_network_tariff",
        ),
    )
