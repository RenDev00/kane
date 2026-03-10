from decimal import Decimal

from pydantic import BaseModel, Field


class StatNumTransactions(BaseModel):
    num_transactions: int = Field(
        default=0,
        description="The number of transactions.",
    )


class StatTotals(BaseModel):
    total_balance: Decimal = Field(
        default=Decimal(0),
        description="The total balance amount.",
    )
    total_income: Decimal = Field(
        default=Decimal(0),
        description="The total income amount.",
    )
    total_expense: Decimal = Field(
        default=Decimal(0),
        description="The total expense amount.",
    )
    total_need: Decimal = Field(
        default=Decimal(0),
        description="The total amount spent on `NEED`s.",
    )
    total_want: Decimal = Field(
        default=Decimal(0),
        description="The total amount spent on `WANTS`s.",
    )
    total_saving: Decimal = Field(
        default=Decimal(0),
        description="The total amount spent on `SAVING`s",
    )
    total_salary: Decimal = Field(
        default=Decimal(0),
        description="The total amount earned through `SALARY`s",
    )
    total_other: Decimal = Field(
        default=Decimal(0),
        description="The total amount earned through `OTHER`s",
    )


class MonthlyStats(BaseModel):
    month: str = Field(
        description="Month identifier in YYYY-MM format.",
        examples=["2025-10"],
    )
    total_income: Decimal = Field(
        default=Decimal(0),
        description="Sum of all income transactions for this month.",
    )
    total_expense: Decimal = Field(
        default=Decimal(0),
        description="Sum of all expense transactions for this month.",
    )
    total_need: Decimal = Field(
        default=Decimal(0),
        description="Sum of all NEED expenses for this month.",
    )
    total_want: Decimal = Field(
        default=Decimal(0),
        description="Sum of all WANT expenses for this month.",
    )
    total_saving: Decimal = Field(
        default=Decimal(0),
        description="Sum of all SAVING expenses for this month.",
    )


class MonthlyStatsResponse(BaseModel):
    months: list[MonthlyStats] = Field(
        default_factory=list,
        description="Monthly statistics sorted chronologically (oldest first).",
    )
