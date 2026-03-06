from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AwareDatetime
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import TransactionDB
from model.transaction import (
    Transaction,
    TransactionCreate,
    TransactionEdit,
    TransactionExpenseCategory,
    TransactionIncomeCategory,
    TransactionType,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "/",
    response_model=Transaction,
    status_code=201,
)
def add_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
) -> Transaction:
    db_obj = TransactionDB(
        amount=transaction.amount,
        date=transaction.date,
        type=transaction.type,
        income_category=(
            transaction.category if transaction.type == TransactionType.INCOME else None
        ),
        expense_category=(
            transaction.category
            if transaction.type == TransactionType.EXPENSE
            else None
        ),
        comment=transaction.comment,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return Transaction.model_validate(db_obj)


@router.get(
    "/",
    response_model=List[Transaction],
)
def get_transactions(
    amount: Optional[float] = Query(
        None,
        ge=0,
    ),
    before: Optional[AwareDatetime] = Query(
        None,
        description="Filter transactions before this datetime (ISO 8601).",
    ),
    after: Optional[AwareDatetime] = Query(
        None,
        description="Filter transactions after this datetime (ISO 8601).",
    ),
    type: Optional[str] = None,
    category: Optional[str] = None,
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[Transaction]:
    stmt = select(TransactionDB)

    if amount is not None:
        stmt = stmt.where(TransactionDB.amount == amount)
    if before is not None:
        stmt = stmt.where(TransactionDB.date <= before)
    if after is not None:
        stmt = stmt.where(TransactionDB.date >= after)
    if type is not None:
        try:
            type = TransactionType[type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=422,
                detail=f"Value error, invalid transaction type {type}.",
            )
        stmt = stmt.where(TransactionDB.type == type)
    if category is not None:
        try:
            category = (
                TransactionIncomeCategory[category.upper()]
                if category.lower() in TransactionIncomeCategory
                else TransactionExpenseCategory[category.upper()]
            )
        except KeyError:
            raise HTTPException(
                status_code=422,
                detail=f"Value error, invalid transaction category {category}.",
            )
        if isinstance(category, TransactionIncomeCategory):
            stmt = stmt.where(TransactionDB.income_category == category)
        else:
            stmt = stmt.where(TransactionDB.expense_category == category)
    if comment is not None:
        stmt = stmt.where(TransactionDB.comment.ilike(f"%{comment}%"))

    objs = db.scalars(stmt).all()
    if not objs:
        raise HTTPException(
            status_code=404,
            detail=f"No matching transactions found.",
        )
    return [Transaction.model_validate(obj) for obj in objs]


@router.get(
    "/{id}",
    response_model=Transaction,
)
def get_transaction_by_id(
    id: int,
    db: Session = Depends(get_db),
) -> Transaction:
    obj = db.get(TransactionDB, id)
    if obj is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with {id=} does not exist.",
        )
    return Transaction.model_validate(obj)


@router.patch(
    "/{id}",
    response_model=Transaction,
)
def edit_transaction_by_id(
    id: int,
    transaction: TransactionEdit,
    db: Session = Depends(get_db),
) -> Transaction:
    dump = transaction.model_dump(exclude_none=True)
    dump.pop("category", None)

    if transaction.type == TransactionType.INCOME:
        dump["income_category"] = transaction.category
        dump["expense_category"] = None
    elif transaction.type == TransactionType.EXPENSE:
        dump["expense_category"] = transaction.category
        dump["income_category"] = None

    stmt = (
        update(TransactionDB)
        .where(TransactionDB.id == id)
        .values(**dump)
        .returning(TransactionDB)
    )
    obj = db.execute(stmt).first()
    db.commit()
    if obj is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with {id=} does not exist.",
        )
    return Transaction.model_validate(obj[0])


@router.delete(
    "/{id}",
    status_code=204,
)
def delete_transaction_by_id(
    id: int,
    db: Session = Depends(get_db),
) -> None:
    deleted = db.query(TransactionDB).filter(TransactionDB.id == id).delete()
    db.commit()
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with {id=} does not exist.",
        )
