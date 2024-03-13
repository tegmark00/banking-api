from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.schemas import IncomingPayment, OutgoingPayment


class BaseEvent(BaseModel):
    pass


class BaseEventWithUUID(BaseEvent):
    id: UUID = Field(default_factory=uuid4)


class Currency(str, Enum):
    EUR = "EUR"


class AccountCreatedEvent(BaseEventWithUUID):
    iban: str = Field(..., min_length=5, max_length=34)
    bic: str = Field(..., min_length=7, max_length=11)
    name: str = Field(..., min_length=1, max_length=255)
    balance: Decimal = Field(0, ge=0, max_digits=12, decimal_places=2)
    currency: Currency = Field(..., min_length=3, max_length=3)


class IncomingPaymentEvent(BaseEventWithUUID, IncomingPayment):
    pass


class OutgoingPaymentEvent(BaseEventWithUUID, OutgoingPayment):
    pass


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
