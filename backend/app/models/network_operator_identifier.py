from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class NetworkOperatorIdentifier(Base):
    __tablename__ = "network_operator_identifiers"

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

    energy_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    zpn_prefix: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        index=True,
    )

    bundesland: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    network_operator: Mapped["NetworkOperator"] = relationship(
        back_populates="identifiers"
    )

    __table_args__ = (
        UniqueConstraint(
            "energy_type",
            "zpn_prefix",
            name="uq_network_operator_identifier_energy_prefix",
        ),
    )
