from typing import Iterable

from fastapi import APIRouter

from app import schemas
from app.dependencies import AccountServiceDep


router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
)


@router.get("/")
async def get_accounts(
        account_service: AccountServiceDep,
) -> Iterable[schemas.AccountRead]:
    return await account_service.get_accounts()


@router.post("/")
async def add_account(
        account: schemas.AccountCreate,
        account_service: AccountServiceDep,
) -> schemas.AccountRead:
    return await account_service.add_account(account)
