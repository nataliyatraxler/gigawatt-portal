from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import require_superadmin
from app.models.user import User
from app.schemas.provider import (
    ProviderCreate,
    ProviderResponse,
    ProviderUpdate,
)
from app.services.provider import (
    create_provider,
    find_provider,
    list_providers,
    update_provider,
)


router = APIRouter(
    prefix="/providers",
    tags=["providers"],
)


@router.get(
    "",
    response_model=list[ProviderResponse],
)
def get_providers(
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return list_providers(db)


@router.get(
    "/{provider_id}",
    response_model=ProviderResponse,
)
def get_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return find_provider(db, provider_id)


@router.post(
    "",
    response_model=ProviderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_provider(
    provider_data: ProviderCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return create_provider(db, provider_data)


@router.patch(
    "/{provider_id}",
    response_model=ProviderResponse,
)
def update_existing_provider(
    provider_id: int,
    provider_data: ProviderUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return update_provider(db, provider_id, provider_data)