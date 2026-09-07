from sqlalchemy.orm import Session

from app.calculator.engine import calculate_tariffs as run_calculation
from app.schemas.calculator import (
    TariffCalculationRequest,
    TariffCalculationResult,
)


def calculate_tariffs(
    db: Session,
    request: TariffCalculationRequest,
) -> list[TariffCalculationResult]:
    return run_calculation(db, request)