import json
import logging

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from sqlalchemy import update

from app.config import app_settings
from app.database import async_session, Account
from app.events import AccountCreatedEvent, TransactionEvent, PaymentType


topics = [
    app_settings.KAFKA_ACCOUNT_CREATED_TOPIC,
    app_settings.KAFKA_TRANSACTION_CREATED_TOPIC
]


consumer = AIOKafkaConsumer(
    *topics,
    bootstrap_servers=app_settings.KAFKA_BOOTSTRAP_SERVERS,
    group_id=app_settings.GROUP_ID,
)


async def consume():
    msg: ConsumerRecord

    async for msg in consumer:

        data = json.loads(msg.value.decode())

        if msg.topic == app_settings.KAFKA_ACCOUNT_CREATED_TOPIC:

            async with async_session() as session:

                account_created_event = AccountCreatedEvent(**data)

                session.add(
                    Account(
                        id=str(account_created_event.id),
                        iban=account_created_event.iban,
                        currency=account_created_event.currency,
                        balance=account_created_event.balance,
                    )
                )

                await session.flush()
                await session.commit()

        elif msg.topic == app_settings.KAFKA_TRANSACTION_CREATED_TOPIC:

            transaction = TransactionEvent(**data)

            if transaction.transaction_type == PaymentType.incoming:
                effective_amount = transaction.amount
            elif transaction.transaction_type == PaymentType.outgoing:
                effective_amount = -transaction.amount
            else:
                logging.error(
                    f"Unknown transaction type: {transaction.transaction_type}"
                )
                continue

            async with async_session() as session:

                await session.execute(
                    update(Account).where(
                        Account.id == transaction.account_id
                    ).values(
                        balance=Account.balance + effective_amount
                    )
                )

                await session.flush()
                await session.commit()

        else:

            pass
