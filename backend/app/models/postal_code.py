from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PostalCode(Base):
    __tablename__ = "postal_codes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    postal_code: Mapped[str] = mapped_column(
        String(10),
        index=True,
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    network_operator_id: Mapped[int] = mapped_column(
        ForeignKey("network_operators.id"),
        nullable=False,
    )

    network_operator: Mapped["NetworkOperator"] = relationship(
        back_populates="postal_codes"
    )