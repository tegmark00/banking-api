from aiokafka import AIOKafkaProducer

from app.config import app_settings


producer = AIOKafkaProducer(
    bootstrap_servers=app_settings.KAFKA_BOOTSTRAP_SERVERS
)


async def get_producer() -> AIOKafkaProducer:
    return producer
