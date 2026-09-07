from sqlalchemy.orm import Session

from app.models.provider import Provider


def get_all_providers(db: Session) -> list[Provider]:
    return db.query(Provider).order_by(Provider.name).all()


def get_provider_by_id(
    db: Session,
    provider_id: int,
) -> Provider | None:
    return (
        db.query(Provider)
        .filter(Provider.id == provider_id)
        .first()
    )


def get_provider_by_name(
    db: Session,
    name: str,
) -> Provider | None:
    return (
        db.query(Provider)
        .filter(Provider.name == name)
        .first()
    )


def save_provider(
    db: Session,
    provider: Provider,
) -> Provider:
    db.add(provider)
    db.commit()
    db.refresh(provider)

    return provider