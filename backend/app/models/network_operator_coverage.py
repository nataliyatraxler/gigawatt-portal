from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class NetworkOperatorCoverage(Base):
    __tablename__ = "network_operator_coverage"

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

    gkz: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    postal_code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    street_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    network_operator: Mapped["NetworkOperator"] = relationship(
        back_populates="coverage_rules"
    )

    __table_args__ = (
        Index(
            "ix_network_operator_coverage_lookup",
            "gkz",
            "postal_code",
            "city",
            "street_code",
        ),
    )
