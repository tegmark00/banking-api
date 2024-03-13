import enum
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

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
        unique=True,
    )

    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(
        String(36),
        default=lambda: str(uuid4()),
        primary_key=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        String(36),
        ForeignKey(Account.id),
    )
    transaction_id: Mapped[UUID] = mapped_column(
        String(36),
    )
    sender_iban: Mapped[str] = mapped_column(
        String(34),
    )
    sender_bic: Mapped[str] = mapped_column(
        String(11),
    )
    sender_name = mapped_column(
        String(255),
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(255),
    )
    currency: Mapped[Currency] = mapped_column(
        String(3),
    )
    purpose = mapped_column(
        String(255),
    )

    account = relationship(Account, back_populates="transactions")


engine = create_async_engine(app_settings.DB_URL)


async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_async_session():
    async with async_session() as session:
        yield session
