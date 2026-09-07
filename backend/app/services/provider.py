from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.provider import Provider
from app.repositories.provider import (
    get_all_providers,
    get_provider_by_id,
    get_provider_by_name,
    save_provider,
)
from app.schemas.provider import ProviderCreate, ProviderUpdate


def list_providers(db: Session) -> list[Provider]:
    return get_all_providers(db)


def find_provider(
    db: Session,
    provider_id: int,
) -> Provider:
    provider = get_provider_by_id(db, provider_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lieferant wurde nicht gefunden.",
        )

    return provider


def create_provider(
    db: Session,
    provider_data: ProviderCreate,
) -> Provider:
    name = provider_data.name.strip()

    if get_provider_by_name(db, name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ein Lieferant mit diesem Namen existiert bereits.",
        )

    provider = Provider(
        name=name,
        website=provider_data.website,
        email=provider_data.email,
        phone=provider_data.phone,
        active=True,
    )

    return save_provider(db, provider)


def update_provider(
    db: Session,
    provider_id: int,
    provider_data: ProviderUpdate,
) -> Provider:
    provider = find_provider(db, provider_id)

    update_data = provider_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        name = update_data["name"].strip()

        existing_provider = get_provider_by_name(db, name)

        if existing_provider and existing_provider.id != provider_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ein Lieferant mit diesem Namen existiert bereits.",
            )

        provider.name = name

    for field in (
        "website",
        "email",
        "phone",
        "active",
    ):
        if field in update_data:
            setattr(provider, field, update_data[field])

    return save_provider(db, provider)