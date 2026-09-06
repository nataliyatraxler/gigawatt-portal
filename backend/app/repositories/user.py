from sqlalchemy.orm import Session

from app.models.user import User


def get_all_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id).all()


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_email_except_id(
    db: Session,
    email: str,
    user_id: int,
) -> User | None:
    return (
        db.query(User)
        .filter(
            User.email == email,
            User.id != user_id,
        )
        .first()
    )


def save_user(
    db: Session,
    user: User,
) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)

    return user