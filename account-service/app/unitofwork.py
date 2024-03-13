from abc import ABC, abstractmethod
from typing import Self, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.repositories import IAccountRepository, AccountRepository


class IUnitOfWork(ABC):
    account_repository: IAccountRepository

    @abstractmethod
    def __init__(self): ...

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


AsyncSessionDep = Annotated[
    AsyncSession,
    Depends(get_async_session)
]


class UnitOfWork(IUnitOfWork):

    def __init__(self, session: AsyncSessionDep):
        self.session = session
        self.account_repository = AccountRepository(self.session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
