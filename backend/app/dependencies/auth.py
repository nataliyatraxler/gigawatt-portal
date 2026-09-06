from fastapi import Depends, HTTPException, status

from app.api.auth import get_current_user
from app.models.user import User, UserRole


def require_superadmin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sie haben keine Berechtigung für diese Aktion.",
        )

    return current_user