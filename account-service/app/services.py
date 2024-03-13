from typing import Iterable

from aiokafka import AIOKafkaProducer
from fastapi import HTTPException

from app import schemas
from app.config import app_settings
from app.repositories import IBANExistsError
from app.unitofwork import IUnitOfWork
from app.events import AccountCreatedEvent, OutgoingPaymentEvent, IncomingPaymentEvent, PaymentType, TransactionEvent


class AccountService:

    def __init__(
            self,
            uow: IUnitOfWork,
            producer: AIOKafkaProducer,
    ):
        self.uow = uow
        self.producer = producer
        self.account_repository = self.uow.account_repository

    async def get_accounts(self) -> Iterable[schemas.AccountRead]:
        return await self.account_repository.get_all()

    async def add_account(self, account: schemas.AccountCreate) -> schemas.AccountRead:
        async with self.uow:

            try:
                created_account: schemas.AccountRead = await self.uow.account_repository.create(account)
            except IBANExistsError:
                raise HTTPException(status_code=400, detail="IBAN already exists")
            await self.uow.commit()

        await self.producer.send(
            topic=app_settings.KAFKA_ACCOUNT_CREATED_TOPIC,
            value=AccountCreatedEvent(**created_account.model_dump()).json().encode(),
        )

        return created_account

    async def handle_incoming_payment(self, payment: IncomingPaymentEvent):

        async with self.uow:

            account = await self.uow.account_repository.update_balance_by_iban(
                iban=payment.receiving_iban,
                amount=payment.amount,
            )

            await self.uow.commit()

        created_transaction = TransactionEvent(
            account_id=account.id,
            payment_id=payment.id,
            transaction_type=PaymentType.incoming,

            sender_iban=payment.sender_iban,
            sender_bic=payment.sender_bic,
            sender_name=payment.sender_name,

            receiving_iban=account.iban,
            receiver_bic=account.bic,
            receiver_name=account.name,

            amount=payment.amount,
            currency=payment.currency,

            reference=payment.reference,
            purpose=payment.purpose,
        )

        await self.producer.send(
            topic=app_settings.KAFKA_TRANSACTION_CREATED_TOPIC,
            value=created_transaction.json().encode(),
        )

    async def handle_outgoing_payment(self, payment: OutgoingPaymentEvent):

        async with self.uow:

            account = await self.uow.account_repository.update_balance_by_iban(
                iban=payment.sender_iban,
                amount=-payment.amount,
            )

            await self.uow.commit()

            created_transaction = TransactionEvent(
                account_id=account.id,
                payment_id=payment.id,
                transaction_type=PaymentType.outgoing,

                sender_iban=account.iban,
                sender_bic=account.bic,
                sender_name=account.name,

                receiving_iban=payment.receiving_iban,
                receiver_bic=payment.receiver_bic,
                receiver_name=payment.receiver_name,

                amount=payment.amount,
                currency=payment.currency,

                reference=payment.reference,
                purpose=payment.purpose,
            )

        await self.producer.send(
            topic=app_settings.KAFKA_TRANSACTION_CREATED_TOPIC,
            value=created_transaction.json().encode(),
        )
