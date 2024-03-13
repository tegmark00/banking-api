import asyncio
from contextlib import asynccontextmanager
from typing import Annotated

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, APIRouter, Response, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import app_settings
from app.consumer import consumer, consume
from app.database import get_async_session, Account
from app.producer import get_producer
from app.schemas import IncomingPayment, OutgoingPayment
from app.events import IncomingPaymentEvent, OutgoingPaymentEvent


router = APIRouter(
    tags=["payments"],
)


AIOKafkaProducerDep = Annotated[
    AIOKafkaProducer,
    Depends(get_producer)
]

AsyncSessionDep = Annotated[
    AsyncSession,
    Depends(get_async_session)
]


@router.post("/incoming-payments")
async def create_incoming_payment(
        payment: IncomingPayment,
        session: AsyncSessionDep,
        producer: AIOKafkaProducerDep
):
    async with session:

        result = await session.execute(
            select(Account).where(
                Account.iban == payment.receiving_iban
            )
        )

        account = result.scalars().first()

        if not account:

            await producer.send(
                topic=app_settings.KAFKA_INCOMING_UNKNOWN_ACCOUNT_TOPIC,
                value=IncomingPaymentEvent(**payment.model_dump()).json().encode(),
            )

            raise HTTPException(status_code=400, detail="No such account")

        account.balance += payment.amount

        await session.merge(account)
        await session.flush()
        await session.commit()

        await producer.send(
            topic=app_settings.KAFKA_INCOMING_PAYMENT_TOPIC,
            value=IncomingPaymentEvent(**payment.model_dump()).json().encode(),
        )

    return Response(status_code=status.HTTP_200_OK)


@router.post("/outgoing-payments")
async def create_outgoing_payment(
        payment: OutgoingPayment,
        producer: AIOKafkaProducerDep,
        session: AsyncSessionDep,
):
    async with session:

        result = await session.execute(
            select(Account).where(
                Account.iban == payment.sender_iban
            )
        )

        account = result.scalars().first()

        if not account:
            await producer.send(
                topic=app_settings.KAFKA_OUTGOING_UNKNOWN_ACCOUNT_TOPIC,
                value=OutgoingPaymentEvent(**payment.model_dump()).json().encode(),
            )
            raise HTTPException(status_code=400, detail="No such account")

        if account.balance < payment.amount:
            await producer.send(
                topic=app_settings.KAFKA_OUTGOING_INSUFFICIENT_FUNDS_TOPIC,
                value=OutgoingPaymentEvent(**payment.model_dump()).json().encode(),
            )
            raise HTTPException(status_code=400, detail="Insufficient funds")

        account.balance -= payment.amount

        await session.merge(account)

        await producer.send(
            topic=app_settings.KAFKA_OUTGOING_PAYMENT_TOPIC,
            value=OutgoingPaymentEvent(**payment.model_dump()).json().encode(),
        )

        await session.flush()
        await session.commit()

    return Response(status_code=status.HTTP_200_OK)


@asynccontextmanager
async def lifespan(_):
    producer = await get_producer()
    await producer.start()
    await consumer.start()
    asyncio.create_task(consume())
    yield
    await consumer.stop()
    await producer.stop()


app = FastAPI(
    title="Payment Service",
    lifespan=lifespan
)

app.include_router(router)
