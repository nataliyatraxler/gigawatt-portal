def calculate_energy_cost(
    consumption_kwh: float,
    work_price_cent_kwh: float,
) -> float:
    return consumption_kwh * work_price_cent_kwh / 100


def calculate_annual_cost_before_bonus(
    base_price_year: float,
    energy_cost: float,
) -> float:
    return base_price_year + energy_cost


def calculate_annual_cost_after_bonus(
    annual_cost_before_bonus: float,
    bonus: float,
) -> float:
    return annual_cost_before_bonus - bonus