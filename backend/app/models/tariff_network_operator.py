from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class TariffNetworkOperator(Base):
    __tablename__ = "tariff_network_operators"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    tariff_id: Mapped[int] = mapped_column(
        ForeignKey("tariffs.id", ondelete="CASCADE"),
        nullable=False,
    )

    network_operator_id: Mapped[int] = mapped_column(
        ForeignKey("network_operators.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "tariff_id",
            "network_operator_id",
            name="uq_tariff_network_operator",
        ),
    )