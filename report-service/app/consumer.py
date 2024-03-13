import json

from aiokafka import AIOKafkaConsumer, ConsumerRecord

from app.config import app_settings
from app.database import async_session, Transaction, Account
from app.events import TransactionEvent, AccountCreatedEvent

topics = [
    app_settings.KAFKA_TRANSACTION_CREATED_TOPIC,
    app_settings.KAFKA_ACCOUNT_CREATED_TOPIC,
]


consumer = AIOKafkaConsumer(
    *topics,
    bootstrap_servers=app_settings.KAFKA_BOOTSTRAP_SERVERS,
    group_id=app_settings.GROUP_ID,
)


async def get_or_create_account(session, account_id: str, iban: str) -> (Account, bool):
    account = await session.get(
        Account,
        account_id
    )

    if not account:
        account = Account(
            id=account_id,
            iban=iban,
        )
        session.add(account)
        await session.flush()
        return account, True

    return account, False


async def consume():
    msg: ConsumerRecord

    async for msg in consumer:

        if msg.topic == app_settings.KAFKA_ACCOUNT_CREATED_TOPIC:

            account = AccountCreatedEvent(**json.loads(msg.value))

            async with async_session() as session:

                account, created = await get_or_create_account(
                    session,
                    str(account.id),
                    account.iban,
                )

                if created:
                    await session.commit()

        if msg.topic == app_settings.KAFKA_TRANSACTION_CREATED_TOPIC:

            transaction = TransactionEvent(**json.loads(msg.value))

            async with async_session() as session:

                account, created = await get_or_create_account(
                    session,
                    str(transaction.account_id),
                    transaction.receiving_iban,
                )

                if created:
                    await session.commit()

                session.add(
                    Transaction(
                        account_id=str(account.id),
                        transaction_id=str(transaction.payment_id),
                        sender_iban=transaction.sender_iban,
                        sender_bic=transaction.sender_bic,
                        sender_name=transaction.sender_name,
                        amount=transaction.amount,
                        currency=transaction.currency,
                        purpose=transaction.purpose,
                    )
                )

                await session.flush()
                await session.commit()
