from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class NetworkOperatorDropdownMapping(Base):
    __tablename__ = "network_operator_dropdown_mappings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    network_operator_identifier_id: Mapped[int] = mapped_column(
        ForeignKey(
            "network_operator_identifiers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    bundesland: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=99,
    )

    standard_visible: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    source_status: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    network_operator_identifier: Mapped["NetworkOperatorIdentifier"] = relationship()

    __table_args__ = (
        UniqueConstraint(
            "network_operator_identifier_id",
            "bundesland",
            name="uq_network_operator_dropdown_identifier_bundesland",
        ),
    )
