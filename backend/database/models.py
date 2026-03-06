from datetime import datetime

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlmodel import func

from database.database import Base
from model.transaction import (
    TransactionExpenseCategory,
    TransactionIncomeCategory,
    TransactionType,
)


class TransactionDB(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.current_timestamp(),
        index=True,
    )
    type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType),
        nullable=False,
        index=True,
    )
    income_category: Mapped[TransactionIncomeCategory | None] = mapped_column(
        SQLEnum(TransactionIncomeCategory),
        nullable=True,
    )
    expense_category: Mapped[TransactionExpenseCategory | None] = mapped_column(
        SQLEnum(TransactionExpenseCategory),
        nullable=True,
    )
    comment: Mapped[str | None] = mapped_column(nullable=True)

    @property
    def category(self) -> TransactionIncomeCategory | TransactionExpenseCategory | None:
        if self.type == TransactionType.INCOME:
            return self.income_category
        if self.type == TransactionType.EXPENSE:
            return self.expense_category
        return None
