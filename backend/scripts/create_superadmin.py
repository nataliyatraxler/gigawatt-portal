import sys
from getpass import getpass
from pathlib import Path

# Allows running: python scripts/create_superadmin.py
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.user import User, UserRole


def create_superadmin():
    db = SessionLocal()

    try:
        email = input("SuperAdmin email: ").strip().lower()
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        password = getpass("Password: ")
        password_confirm = getpass("Confirm password: ")

        if not email:
            print("Email cannot be empty.")
            return

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            return

        if password != password_confirm:
            print("Passwords do not match.")
            return

        existing_user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_user:
            print(f"User {email} already exists.")
            return

        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name or None,
            last_name=last_name or None,
            role=UserRole.SUPERADMIN,
            provider_id=None,
            active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print()
        print("SuperAdmin created successfully!")
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role.value}")

    except Exception as exc:
        db.rollback()
        print(f"Error creating SuperAdmin: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_superadmin()
