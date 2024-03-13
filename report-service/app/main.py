import asyncio
import csv
import io
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.consumer import consumer, consume
from app.database import get_async_session, Account, Transaction


@asynccontextmanager
async def lifespan(_):
    await consumer.start()
    asyncio.create_task(consume())
    yield
    await consumer.stop()


app = FastAPI(
    title="Report Service",
    lifespan=lifespan,
)


AsyncSessionDep = Annotated[
    AsyncSession,
    Depends(get_async_session)
]


@app.get("/reports/{account_id}/csv", responses={404: {"description": "Report not found"}})
async def export_csv_by_iban(account_id: str, session: AsyncSessionDep):
    account = await session.execute(
        select(
            Account
        ).where(
            Account.id == account_id
        )
    )

    if not account.scalars().first():
        return Response(status_code=404)

    rows = await session.execute(
        select(
            Transaction, Account
        ).join(
            Transaction.account
        )
    )

    def iter_file():

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow([
            'IBAN',
            'TRANSACTION_ID',
            'SENDER_IBAN',
            'SENDER_BIC',
            'SENDER_NAME',
            'AMOUNT',
            'CURRENCY',
            'PURPOSE',
        ])

        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        for row in rows:

            writer.writerow([
                row.Account.iban,
                row.Transaction.id,
                row.Transaction.sender_iban,
                row.Transaction.sender_bic,
                row.Transaction.sender_name,
                row.Transaction.amount,
                row.Transaction.currency,
                row.Transaction.purpose,
            ])

            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    return StreamingResponse(
        content=iter_file(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={account_id}.csv"}
    )
