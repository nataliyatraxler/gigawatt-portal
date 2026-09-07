from sqlalchemy.orm import Session

from app.models.tariff import Tariff


def get_all_tariffs(db: Session) -> list[Tariff]:
    return db.query(Tariff).order_by(Tariff.id).all()


def get_tariff_by_id(
    db: Session,
    tariff_id: int,
) -> Tariff | None:
    return (
        db.query(Tariff)
        .filter(Tariff.id == tariff_id)
        .first()
    )


def get_tariffs_by_provider(
    db: Session,
    provider_id: int,
) -> list[Tariff]:
    return (
        db.query(Tariff)
        .filter(Tariff.provider_id == provider_id)
        .order_by(Tariff.name)
        .all()
    )


def save_tariff(
    db: Session,
    tariff: Tariff,
) -> Tariff:
    db.add(tariff)
    db.commit()
    db.refresh(tariff)

    return tariff