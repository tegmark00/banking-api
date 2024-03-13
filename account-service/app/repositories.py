from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TypeVar, Generic, Iterable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Account
from app.schemas import AccountCreate, AccountRead


R = TypeVar('R')
C = TypeVar('C')


class IAccountRepository(ABC, Generic[R, C]):

    @abstractmethod
    async def get_all(self) -> Iterable[R]:
        pass

    @abstractmethod
    async def create(self, instance: C) -> R:
        pass

    @abstractmethod
    async def update_balance_by_iban(self, iban: str, amount: Decimal) -> R:
        pass


class IBANExistsError(Exception):
    pass


class AccountWithIBANDoesNotExistError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class AccountRepository(
    IAccountRepository[
        AccountRead,
        AccountCreate,
    ]
):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> Iterable[AccountRead]:
        accounts = await self.session.execute(select(Account))
        return (AccountRead(**account.__dict__) for account in accounts.scalars())

    async def create(self, instance: AccountCreate) -> AccountRead:
        account_model = Account(**instance.dict())

        self.session.add(account_model)

        try:
            await self.session.flush()
        except IntegrityError:
            raise IBANExistsError

        await self.session.refresh(account_model)

        return AccountRead(**account_model.__dict__)

    async def update_balance_by_iban(self, iban: str, amount: int) -> AccountRead:
        accounts = await self.session.execute(select(Account).where(Account.iban == iban))
        account = accounts.scalars().first()

        if not account:
            raise AccountWithIBANDoesNotExistError

        account.balance += amount

        if account.balance < 0:
            raise InsufficientFundsError

        await self.session.merge(account)
        await self.session.flush()

        return AccountRead(**account.__dict__)
