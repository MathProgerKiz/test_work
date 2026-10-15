from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class IndexPriceCreate(BaseModel):
    ticker: Literal["btc_usd", "eth_usd"]
    price: Decimal = Field(gt=0)
    timestamp: int = Field(ge=0)


class IndexPriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    price: Decimal
    timestamp: int
