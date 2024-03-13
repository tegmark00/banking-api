from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    pass


class Currency(str, Enum):
    EUR = "EUR"


class IncomingPayment(BaseSchema):
    sender_iban: str
    sender_name: str
    sender_bic: str
    receiving_iban: str
    external_id: str
    amount: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    currency: Currency = Field(..., min_length=3, max_length=3)
    reference: str
    purpose: str


# Not sure if we need sender name as we have it in the account
class OutgoingPayment(BaseSchema):
    sender_iban: str
    receiving_iban: str
    receiver_bic: str
    receiver_name: str
    amount: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    currency: Currency = Field(..., min_length=3, max_length=3)
    reference: str
    purpose: str
