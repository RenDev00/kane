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


def _validate_amount(v: Decimal) -> Decimal:
    if v < 0:
        raise ValueError("Transaction amount must be positive.")
    return v


def _validate_type(v: str | TransactionType) -> TransactionType:
    op = {
        str: lambda x: TransactionType[x.upper()],
        TransactionType: lambda x: x,
    }
    try:
        return op[type(v)](v)
    except KeyError:
        raise ValueError(f"Invalid transaction type {v}.")


def _validate_category(v: str | TransactionCategory) -> TransactionCategory:
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
        return op[type(v)](v)
    except KeyError:
        raise ValueError(f"Invalid transaction category {v}.")


def _validate_type_category_combo(
    type_: TransactionType, category: TransactionCategory
) -> None:
    if (
        type_ is TransactionType.EXPENSE
        and type(category) is TransactionIncomeCategory
        or type_ is TransactionType.INCOME
        and type(category) is TransactionExpenseCategory
    ):
        raise ValueError(
            f"Transactions with type={type_.value} cannot have category={category.value}."
        )


class TransactionBase(BaseModel):
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

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return _validate_amount(v)

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: str | TransactionType) -> TransactionType:
        return _validate_type(v)

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: str | TransactionCategory) -> TransactionCategory:
        return _validate_category(v)

    @model_validator(mode="after")
    def validate(self) -> Self:
        _validate_type_category_combo(self.type, self.category)
        return self


class Transaction(TransactionBase):
    id: int | None = Field(
        default=None,
        examples=[1, 2, 3],
        description="A unique transaction identifier (auto-generated on create).",
        frozen=True,
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TransactionCreate(TransactionBase):
    model_config = ConfigDict(
        populate_by_name=True,
    )


class TransactionEdit(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    amount: Optional[Decimal] = Field(
        default=None,
        examples=[19.99, None],
        description="The value of the transaction.",
    )
    date: Optional[AwareDatetime] = Field(
        default=None,
        examples=["2026-03-02T20:50:32Z", None],
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
        default=None,
        examples=["Groceries", "Insurance", "Electricity Bill", None],
        description="An optional transaction comment.",
    )

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v is None:
            return v
        return _validate_amount(v)

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(
        cls, v: Optional[str | TransactionType]
    ) -> Optional[TransactionType]:
        if v is None:
            return v
        return _validate_type(v)

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(
        cls, v: Optional[str | TransactionCategory]
    ) -> Optional[TransactionCategory]:
        if v is None:
            return v
        return _validate_category(v)

    @model_validator(mode="after")
    def validate(self) -> Self:
        if self.type is not None and self.category is not None:
            _validate_type_category_combo(self.type, self.category)
        return self
