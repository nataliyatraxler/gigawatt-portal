from sqlalchemy.orm import Query

from app.models.tariff import Tariff
from app.models.tariff_network_operator import TariffNetworkOperator


def apply_tariff_filters(
    query: Query,
    energy_type: str,
    customer_type: str,
    network_operator_id: int,
    provider_id: int | None = None,
) -> Query:
    query = (
        query.join(
            TariffNetworkOperator,
            TariffNetworkOperator.tariff_id == Tariff.id,
        )
        .filter(
            Tariff.active.is_(True),
            Tariff.energy_type == energy_type,
            Tariff.customer_type == customer_type,
            TariffNetworkOperator.network_operator_id == network_operator_id,
        )
    )

    if provider_id is not None:
        query = query.filter(
            Tariff.provider_id == provider_id
        )

    return query