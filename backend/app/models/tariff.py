from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    provider_id: Mapped[int] = mapped_column(
        ForeignKey("providers.id"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    energy_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    customer_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    base_price_year: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    work_price_cent_kwh: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    night_price_cent_kwh: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    bonus: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )

    contract_months: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    price_guarantee_months: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    green_energy: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    digital_signature: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    valid_from: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    valid_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    provider: Mapped["Provider"] = relationship(
        back_populates="tariffs"
    )