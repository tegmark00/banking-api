from typing import Annotated

from aiokafka import AIOKafkaProducer
from fastapi import Depends

from app.producer import get_producer
from app.services import AccountService
from app.unitofwork import IUnitOfWork, UnitOfWork


AIOKafkaProducerDep = Annotated[
    AIOKafkaProducer,
    Depends(get_producer)
]


UnitOfWorkDep = Annotated[
    IUnitOfWork,
    Depends(UnitOfWork)
]


def account_service(
        uow: UnitOfWorkDep,
        producer: AIOKafkaProducerDep
) -> AccountService:
    return AccountService(
        uow=uow,
        producer=producer
    )


AccountServiceDep = Annotated[
    AccountService,
    Depends(account_service)
]
