from decimal import Decimal
from enum import StrEnum, auto
from typing import Optional, Self, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
    AwareDatetime,
)


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

    id: int | None = Field(
        default=None,
        examples=[1, 2, 3],
        description="A unique transaction identifier (auto-generated on create).",
        frozen=True,
    )
    amount: Decimal = Field(
        examples=[19.99],
        description="The value of the transaction.",
    )
    date: AwareDatetime = Field(
        examples=["2026-03-02T20:50:32Z"],
        description="The date of the transaction.",
    )
    type: TransactionType = Field(
        examples=["EXPENSE", "INCOME"],
        description="The type of the transaction.",
    )
    category: TransactionCategory = Field(
        examples=["NEED", "WANT", "SAVING", "SALARY", "OTHER"],
        description="Income: SALARY or OTHER. Expense: NEED, WANT or SAVING",
    )
    comment: Optional[str] = Field(
        examples=["Groceries", "Insurance", "Electricity Bill", None],
        description="An optional transaction comment.",
        default=None,
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Transaction amount must be positive.")
        return v

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: str | TransactionType) -> TransactionType:
        op = {
            str: lambda x: TransactionType[x.upper()],
            TransactionType: lambda x: x,
        }
        try:
            transaction_type = op[type(v)](v)
        except KeyError:
            raise ValueError(f"Invalid transaction type {v}.")

        return transaction_type

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: str | TransactionCategory) -> TransactionCategory:
        if isinstance(v, TransactionCategory):
            return v

        op = {
            str: lambda x: (
                TransactionIncomeCategory[x.upper()]
                if x.lower() in TransactionIncomeCategory
                else TransactionExpenseCategory[x.upper()]
            ),
        }
        try:
            transaction_category = op[type(v)](v)
        except KeyError:
            raise ValueError(f"Invalid transaction category {v}.")

        return transaction_category

    @model_validator(mode="after")
    def validate(self) -> Self:
        if (
            self.type is TransactionType.EXPENSE
            and type(self.category) is TransactionIncomeCategory
            or self.type is TransactionType.INCOME
            and type(self.category) is TransactionExpenseCategory
        ):
            raise ValueError(
                f"Transactions with type={self.type.value} cannot have category={self.category.value}."
            )

        return self
