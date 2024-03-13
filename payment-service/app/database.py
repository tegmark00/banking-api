import enum
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import String, Numeric, Enum
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import app_settings


class Currency(enum.Enum):
    EUR = "EUR"


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(
        String(36),
        default=lambda: str(uuid4()),
        primary_key=True,
    )
    iban: Mapped[str] = mapped_column(
        String(34),
        unique=True
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
    )
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency),
        default=Currency.EUR,

    )


engine = create_async_engine(
    app_settings.DB_URL
)


async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_async_session():
    async with async_session() as session:
        yield session
