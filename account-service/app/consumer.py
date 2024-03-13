import json

from aiokafka import AIOKafkaConsumer, ConsumerRecord

from app.config import app_settings
from app.database import async_session
from app.events import IncomingPaymentEvent, OutgoingPaymentEvent
from app.producer import get_producer
from app.services import AccountService
from app.unitofwork import UnitOfWork


topics = [
    app_settings.KAFKA_INCOMING_PAYMENT_TOPIC,
    app_settings.KAFKA_OUTGOING_PAYMENT_TOPIC,
]


consumer = AIOKafkaConsumer(
    *topics,
    bootstrap_servers=app_settings.KAFKA_BOOTSTRAP_SERVERS,
    group_id=app_settings.GROUP_ID,
)


async def consume():
    producer = await get_producer()
    msg: ConsumerRecord

    async for msg in consumer:

        data = json.loads(msg.value.decode())

        if msg.topic == app_settings.KAFKA_INCOMING_PAYMENT_TOPIC:

            incoming_payment = IncomingPaymentEvent(**data)

            async with async_session() as session:
                async with UnitOfWork(session) as uow:
                    account_service = AccountService(uow=uow, producer=producer)
                    await account_service.handle_incoming_payment(incoming_payment)

        elif msg.topic == app_settings.KAFKA_OUTGOING_PAYMENT_TOPIC:

            outgoing_payment = OutgoingPaymentEvent(**data)

            async with async_session() as session:
                async with UnitOfWork(session) as uow:
                    account_service = AccountService(uow=uow, producer=producer)
                    await account_service.handle_outgoing_payment(outgoing_payment)

        else:

            pass
