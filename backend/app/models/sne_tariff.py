from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SneTariff(Base):
    __tablename__ = "sne_tariffs"

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

    network_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    tariff_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    network_area: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    lp_cent: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    ap_cent_kwh: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    snap_cent_kwh: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    dtap_cent_kwh: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    dnap_cent_kwh: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    network_loss_cent_kwh: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "year",
            "network_level",
            "tariff_type",
            "network_area",
            name="uq_sne_tariff",
        ),
    )
