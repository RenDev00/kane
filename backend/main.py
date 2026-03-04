from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException

from model.transaction import (
    Transaction,
    TransactionCategory,
    TransactionType,
)

app = FastAPI()


data = {
    0: Transaction(
        id=0,
        amount=19.99,
        date="2026-03-02T20:50:32",
        type="income",
        category="salary",
        comment="Test Transaction",
    ),
    1: Transaction(
        id=1,
        amount=9.99,
        date="2026-02-02T20:50:32",
        type="expense",
        category="want",
    ),
}


@app.get("/transactions/")
async def get_transactions(
    amount: Optional[float] = None,
    before: Optional[datetime] = None,
    after: Optional[datetime] = None,
    type: Optional[TransactionType] = None,
    category: Optional[TransactionCategory] = None,
    comment: Optional[str] = None,
) -> List[Transaction]:
    def check_transaction(t: Transaction):
        return all(
            [
                amount is None or t.amount == amount,
                before is None or t.date <= before,
                after is None or t.date >= after,
                type is None or t.type == type,
                category is None or t.category == category,
                comment is None or t.comment == comment,
            ]
        )

    return [t for t in data.values() if check_transaction(t)]


@app.get("/transactions/{id}")
async def get_transaction_by_id(id: int) -> Transaction:
    if id not in data.keys():
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with {id=} does not exist.",
        )
    return data[id]
