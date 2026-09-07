from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.calculator import (
    TariffCalculationRequest,
    TariffCalculationResult,
)
from app.services.calculator import calculate_tariffs


router = APIRouter(
    prefix="/calculator",
    tags=["tarifrechner"],
)


@router.post(
    "/tariffs",
    response_model=list[TariffCalculationResult],
)
def calculate_available_tariffs(
    request: TariffCalculationRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return calculate_tariffs(db, request)