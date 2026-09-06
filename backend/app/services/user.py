from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import (
    get_all_users,
    get_user_by_email,
    get_user_by_email_except_id,
    get_user_by_id,
    save_user,
)
from app.schemas.user import UserCreate, UserUpdate


def list_users(db: Session) -> list[User]:
    return get_all_users(db)


def find_user(
    db: Session,
    user_id: int,
) -> User:
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benutzer wurde nicht gefunden.",
        )

    return user


def create_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    email = str(user_data.email).lower()

    if get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.",
        )

    user = User(
        email=email,
        password_hash=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        provider_id=user_data.provider_id,
        active=True,
    )

    return save_user(db, user)


def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate,
) -> User:
    user = find_user(db, user_id)

    update_data = user_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        email = str(update_data["email"]).lower()

        existing_user = get_user_by_email_except_id(
            db,
            email,
            user_id,
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.",
            )

        user.email = email

    if "password" in update_data:
        user.password_hash = hash_password(
            update_data["password"]
        )

    for field in (
        "first_name",
        "last_name",
        "role",
        "provider_id",
        "active",
    ):
        if field in update_data:
            setattr(user, field, update_data[field])

    return save_user(db, user)