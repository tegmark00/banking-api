from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_ACCOUNT_CREATED_TOPIC: str
    KAFKA_TRANSACTION_CREATED_TOPIC: str
    KAFKA_INCOMING_PAYMENT_TOPIC: str
    KAFKA_OUTGOING_PAYMENT_TOPIC: str

    GROUP_ID: str = "account-service"

    model_config = SettingsConfigDict(env_file=".env")


app_settings = Settings()
