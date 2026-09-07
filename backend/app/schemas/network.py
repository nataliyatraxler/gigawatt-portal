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
    network_operator_id: int


class PostalCodeResponse(BaseModel):
    id: int
    postal_code: str
    city: str
    network_operator_id: int

    model_config = {
        "from_attributes": True
    }