from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    tariffs: Mapped[list["Tariff"]] = relationship(
        back_populates="provider"
    )