from datetime import datetime, timezone

from sqlalchemy import DateTime, Dialect, Enum as SQLEnum, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column
from sqlmodel import func

from database.database import Base
from model.transaction import (
    TransactionExpenseCategory,
    TransactionIncomeCategory,
    TransactionType,
)


class UTCDateTime(TypeDecorator):
    """Convert aware -> naive UTC when saving, naive UTC -> aware when loading"""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime, dialect: Dialect) -> datetime:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value: datetime, dialect: Dialect) -> datetime:
        return value.replace(tzinfo=timezone.utc)


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
        UTCDateTime,
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
