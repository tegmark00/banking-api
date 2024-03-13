from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class Currency(str, Enum):
    EUR = "EUR"


class BaseSchema(BaseModel):
    pass


class AccountCreate(BaseSchema):
    iban: str = Field(..., min_length=5, max_length=34)
    bic: str = Field(..., min_length=7, max_length=11)
    name: str = Field(..., min_length=1, max_length=255)
    balance: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    currency: Currency = Field(..., min_length=3, max_length=3)


class AccountRead(AccountCreate):
    id: UUID
