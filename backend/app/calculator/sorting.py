from app.schemas.calculator import TariffCalculationResult


def sort_by_annual_cost(
    results: list[TariffCalculationResult],
) -> list[TariffCalculationResult]:
    return sorted(
        results,
        key=lambda item: item.annual_cost_after_bonus,
    )