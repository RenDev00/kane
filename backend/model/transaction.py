from datetime import datetime
from enum import StrEnum, auto
from typing import Optional, Self, Union

from pydantic import BaseModel, Field, model_validator


class TransactionType(StrEnum):
    INCOME = auto()
    EXPENSE = auto()


class TransactionExpenseCategory(StrEnum):
    NEED = auto()
    WANT = auto()
    SAVING = auto()


class TransactionIncomeCategory(StrEnum):
    SALARY = auto()
    OTHER = auto()


TransactionCategory = Union[TransactionExpenseCategory, TransactionIncomeCategory]


class Transaction(BaseModel):
    """
    Transaction model.
    """

    id: int = Field(
        examples=[0, 1, 2], description="A unique transaction identifier.", frozen=True
    )
    amount: float = Field(examples=[19.99], description="The value of the transaction.")
    date: datetime = Field(
        examples=["2026-03-02T20:50:32Z"], description="The date of the transaction."
    )
    type: TransactionType = Field(
        examples=["INCOME", "EXPENSE"], description="The type of the transaction."
    )
    category: TransactionCategory = Field(
        examples=["NEED", "WANT", "SAVING", "SALARY", "OTHER"],
        description="The category of the transaction. Income transactions must be of categories SALARY, or OTHER. Expense transactions must be of categories NEED, WANT, or SAVING",
    )
    comment: Optional[str] = Field(
        examples=["Groceries", "Insurance", "Electricity Bill", None],
        description="An optional transaction comment.",
        default=None,
    )

    @model_validator(mode="after")
    def validate(self) -> Self:
        if (
            self.type is TransactionType.EXPENSE
            and type(self.category) is TransactionIncomeCategory
            or self.type is TransactionType.INCOME
            and type(self.category) is TransactionExpenseCategory
        ):
            raise ValueError(
                f"Transactions with type={self.type.name} cannot have category={self.category.name}."
            )

        return self
