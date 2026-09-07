from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class NetworkOperator(Base):
    __tablename__ = "network_operators"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    code: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    postal_codes: Mapped[list["PostalCode"]] = relationship(
        back_populates="network_operator"
    )