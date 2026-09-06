from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import require_superadmin
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import (
    create_user,
    find_user,
    list_users,
    update_user,
)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return list_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return find_user(db, user_id)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return create_user(db, user_data)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_existing_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    return update_user(db, user_id, user_data)