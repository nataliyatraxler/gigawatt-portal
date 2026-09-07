from pydantic import BaseModel


class TariffNetworkResponse(BaseModel):
    id: int
    tariff_id: int
    network_operator_id: int

    model_config = {
        "from_attributes": True
    }