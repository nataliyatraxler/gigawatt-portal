from pydantic import BaseModel, Field


class NetworkOperatorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str | None = Field(default=None, max_length=100)


class NetworkOperatorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, max_length=100)
    active: bool | None = None


class NetworkOperatorResponse(BaseModel):
    id: int
    name: str
    code: str | None
    active: bool

    model_config = {
        "from_attributes": True
    }

class PostalCodeCreate(BaseModel):
    postal_code: str = Field(min_length=4, max_length=10)
    city: str = Field(min_length=1, max_length=255)
    gkz: str | None = Field(default=None, max_length=10)
    municipality: str | None = Field(default=None, max_length=255)
    network_operator_id: int | None = None

class PostalCodeResponse(BaseModel):
    id: int
    postal_code: str
    city: str
    gkz: str | None
    municipality: str | None
    network_operator_id: int | None

    model_config = {
        "from_attributes": True
    }

class NetworkOperatorIdentifierResponse(BaseModel):
    network_operator_id: int
    network_operator_name: str
    energy_type: str
    zpn_prefix: str
    bundesland: str
