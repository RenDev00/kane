from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AwareDatetime
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import TransactionDB
from model.stats import (
    MonthlyStats,
    MonthlyStatsResponse,
    StatNumTransactions,
    StatTotals,
)
from model.transaction import (
    TransactionExpenseCategory,
    TransactionIncomeCategory,
    TransactionType,
)


router = APIRouter(prefix="/stats", tags=["stats"])


def _stmt_helper(
    stmt,
    before=None,
    after=None,
    type=None,
    category=None,
    comment=None,
):
    if before:
        stmt = stmt.where(TransactionDB.date <= before)
    if after:
        stmt = stmt.where(TransactionDB.date >= after)
    if type:
        try:
            type = TransactionType[type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=422,
                detail=f"Value error, invalid transaction type {type}.",
            )
        stmt = stmt.where(TransactionDB.type == type)
    if category:
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
    if comment:
        stmt = stmt.where(TransactionDB.comment.ilike(f"%{comment}%"))
    return stmt


@router.get(
    "/num_transactions",
    response_model=StatNumTransactions,
)
def get_number_of_transactions(
    before: Optional[AwareDatetime] = Query(
        None,
        description="Filter transactions before this datetime (ISO 8601).",
    ),
    after: Optional[AwareDatetime] = Query(
        None,
        description="Filter transactions after this datetime (ISO 8601).",
    ),
    type: Optional[str] = Query(
        None,
        description="Filter transactions based on the provided type.",
    ),
    category: Optional[str] = Query(
        None,
        description="Filter transactions based on the provided category.",
    ),
    comment: Optional[str] = Query(
        None,
        description="Filter transactions based on the provided comment.",
    ),
    db: Session = Depends(get_db),
) -> StatNumTransactions:
    stmt = select(func.count()).select_from(TransactionDB)
    stmt = _stmt_helper(
        stmt,
        before=before,
        after=after,
        type=type,
        category=category,
        comment=comment,
    )
    num = db.scalar(stmt) or 0
    return StatNumTransactions(num_transactions=num)


@router.get(
    "/totals",
    response_model=StatTotals,
)
def get_total_transaction_amounts(
    before: Optional[AwareDatetime] = Query(
        None,
        description="Filter transactions before this datetime (ISO 8601).",
    ),
    after: Optional[AwareDatetime] = Query(
        None,
        description="Filter transactions after this datetime (ISO 8601).",
    ),
    db: Session = Depends(get_db),
) -> StatTotals:
    stmt = select(
        func.sum(
            case(
                (
                    TransactionDB.type == TransactionType.INCOME,
                    TransactionDB.amount,
                ),
                else_=0,
            )
        ).label("total_income"),
        func.sum(
            case(
                (
                    TransactionDB.type == TransactionType.EXPENSE,
                    TransactionDB.amount,
                ),
                else_=0,
            )
        ).label("total_expense"),
        func.sum(
            case(
                (
                    TransactionDB.expense_category == TransactionExpenseCategory.NEED,
                    TransactionDB.amount,
                ),
                else_=0,
            )
        ).label("total_need"),
        func.sum(
            case(
                (
                    TransactionDB.expense_category == TransactionExpenseCategory.WANT,
                    TransactionDB.amount,
                ),
                else_=0,
            )
        ).label("total_want"),
        func.sum(
            case(
                (
                    TransactionDB.expense_category == TransactionExpenseCategory.SAVING,
                    TransactionDB.amount,
                ),
                else_=0,
            )
        ).label("total_saving"),
        func.sum(
            case(
                (
                    TransactionDB.income_category == TransactionIncomeCategory.SALARY,
                    TransactionDB.amount,
                ),
                else_=0,
            )
        ).label("total_salary"),
        func.sum(
            case(
                (
                    TransactionDB.income_category == TransactionIncomeCategory.OTHER,
                    TransactionDB.amount,
                ),
                else_=0,
            )
        ).label("total_other"),
    )

    stmt = _stmt_helper(
        stmt,
        before=before,
        after=after,
    )
    res = db.execute(stmt).one()

    total_income = res.total_income
    total_expense = res.total_expense

    if total_income and total_expense:
        balance = total_income - total_expense
    elif total_expense:
        balance = total_expense * (-1)
    elif total_income:
        balance = total_income
    else:
        balance = Decimal(0)

    return StatTotals(
        total_balance=balance,
        total_income=total_income or Decimal(0),
        total_expense=total_expense or Decimal(0),
        total_need=res.total_need or Decimal(0),
        total_want=res.total_want or Decimal(0),
        total_saving=res.total_saving or Decimal(0),
        total_salary=res.total_salary or Decimal(0),
        total_other=res.total_other or Decimal(0),
    )


def _month_start(year: int, month: int) -> datetime:
    return datetime(year, month, 1, tzinfo=timezone.utc)


def _add_months(dt: datetime, n: int) -> datetime:
    year = dt.year
    month = dt.month + n
    while month > 12:
        month -= 12
        year += 1
    return _month_start(year, month)


def _subtract_months(dt: datetime, n: int) -> datetime:
    year = dt.year
    month = dt.month - n
    while month <= 0:
        month += 12
        year -= 1
    return _month_start(year, month)


@router.get(
    "/monthly",
    response_model=MonthlyStatsResponse,
)
def get_monthly_stats(
    months: int = Query(
        6,
        ge=1,
        description="Number of months to return.",
    ),
    before: Optional[AwareDatetime] = Query(
        None,
        description="ISO 8601 datetime. Returns months strictly before this date.",
    ),
    db: Session = Depends(get_db),
) -> MonthlyStatsResponse:
    now = datetime.now(timezone.utc)
    before_dt = before if before else now

    first_of_before_month = _month_start(before_dt.year, before_dt.month)
    is_partial_month = before_dt > first_of_before_month

    if is_partial_month:
        upper_filter = before_dt
        upper_timeline = _add_months(first_of_before_month, 1)
    else:
        upper_filter = first_of_before_month
        upper_timeline = first_of_before_month

    lower = _subtract_months(upper_timeline, months)

    month_label = func.strftime("%Y-%m", TransactionDB.date)
    stmt = (
        select(
            month_label.label("month"),
            func.sum(
                case(
                    (
                        TransactionDB.type == TransactionType.INCOME,
                        TransactionDB.amount,
                    ),
                    else_=0,
                )
            ).label("total_income"),
            func.sum(
                case(
                    (
                        TransactionDB.type == TransactionType.EXPENSE,
                        TransactionDB.amount,
                    ),
                    else_=0,
                )
            ).label("total_expense"),
            func.sum(
                case(
                    (
                        TransactionDB.expense_category
                        == TransactionExpenseCategory.NEED,
                        TransactionDB.amount,
                    ),
                    else_=0,
                )
            ).label("total_need"),
            func.sum(
                case(
                    (
                        TransactionDB.expense_category
                        == TransactionExpenseCategory.WANT,
                        TransactionDB.amount,
                    ),
                    else_=0,
                )
            ).label("total_want"),
            func.sum(
                case(
                    (
                        TransactionDB.expense_category
                        == TransactionExpenseCategory.SAVING,
                        TransactionDB.amount,
                    ),
                    else_=0,
                )
            ).label("total_saving"),
        )
        .where(TransactionDB.date >= lower)
        .where(TransactionDB.date < upper_filter)
        .group_by(month_label)
    )

    rows = db.execute(stmt).all()
    db_months = {row.month: row for row in rows}

    result: list[MonthlyStats] = []
    for i in range(months):
        m = _subtract_months(upper_timeline, months - i)
        key = m.strftime("%Y-%m")
        if key in db_months:
            row = db_months[key]
            result.append(
                MonthlyStats(
                    month=key,
                    total_income=row.total_income or Decimal(0),
                    total_expense=row.total_expense or Decimal(0),
                    total_need=row.total_need or Decimal(0),
                    total_want=row.total_want or Decimal(0),
                    total_saving=row.total_saving or Decimal(0),
                )
            )
        else:
            result.append(MonthlyStats(month=key))

    return MonthlyStatsResponse(months=result)
