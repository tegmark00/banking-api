from decimal import Decimal
from uuid import UUID, uuid4
from enum import Enum
from pydantic import Field, BaseModel

from app.schemas import AccountRead


class BaseEvent(BaseModel):
    pass


class BaseEventWithUUID(BaseEvent):
    id: UUID = Field(default_factory=uuid4)


class AccountCreatedEvent(BaseEvent, AccountRead):
    pass


class Currency(str, Enum):
    EUR = "EUR"


class OutgoingPaymentEvent(BaseEventWithUUID):
    sender_iban: str
    receiving_iban: str
    receiver_bic: str
    receiver_name: str
    amount: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    currency: Currency = Field(..., min_length=3, max_length=3)
    reference: str
    purpose: str


class IncomingPaymentEvent(BaseEventWithUUID):
    sender_iban: str
    sender_name: str
    sender_bic: str
    receiving_iban: str
    external_id: str
    amount: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    currency: Currency = Field(..., min_length=3, max_length=3)
    reference: str
    purpose: str


class PaymentType(str, Enum):
    incoming = "incoming"
    outgoing = "outgoing"


class TransactionEvent(BaseEventWithUUID):
    account_id: UUID
    payment_id: UUID

    transaction_type: PaymentType

    sender_iban: str
    sender_bic: str
    sender_name: str

    receiving_iban: str
    receiver_bic: str
    receiver_name: str

    amount: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    currency: Currency = Field(..., min_length=3, max_length=3)

    reference: str
    purpose: str
