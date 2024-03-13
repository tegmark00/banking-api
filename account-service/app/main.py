import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.producer import producer
from app.consumer import (
    consumer,
    consume
)
from app.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await producer.start()
    await consumer.start()
    asyncio.create_task(consume())
    yield
    await producer.stop()
    await consumer.stop()


app = FastAPI(
    title="Account Service",
    lifespan=lifespan
)

app.include_router(
    router,
    prefix="/v1"
)
