from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import AwareDatetime

from model.transaction import (
    Transaction,
    TransactionCategory,
    TransactionExpenseCategory,
    TransactionIncomeCategory,
    TransactionType,
)

app = FastAPI()


data = {
    0: Transaction(
        id=0,
        amount=19.99,
        date="2026-03-02T20:50:32Z",
        type=TransactionType.INCOME,
        category=TransactionIncomeCategory.SALARY,
        comment="Test Transaction",
    ),
    1: Transaction(
        id=1,
        amount=9.99,
        date="2026-02-02T20:50:32Z",
        type=TransactionType.EXPENSE,
        category=TransactionExpenseCategory.NEED,
    ),
}


@app.put("/transactions/")
def add_transaction(transaction: Transaction) -> Dict[str, str | Transaction]:
    data[len(data)] = transaction
    return {
        "message": "Transaction added",
        "transaction": transaction,
    }


@app.get("/transactions/")
def get_transactions(
    amount: Optional[float] = None,
    before: Optional[AwareDatetime] = None,
    after: Optional[AwareDatetime] = None,
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
                comment is None
                or t.comment is not None
                and comment.lower() in t.comment.lower(),
            ]
        )

    return [t for t in data.values() if check_transaction(t)]


@app.get("/transactions/{id}")
def get_transaction_by_id(id: int) -> Transaction:
    if id not in data.keys():
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with {id=} does not exist.",
        )
    return data[id]
