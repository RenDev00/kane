from datetime import datetime, timezone
from typing import List

import pytest
from fastapi.testclient import TestClient

from main import app
from model.transaction import (
    Transaction,
    TransactionExpenseCategory,
    TransactionIncomeCategory,
    TransactionType,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_income_transaction() -> Transaction:
    return Transaction(
        id=1,
        amount=5000.00,
        date=datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        type=TransactionType.INCOME,
        category=TransactionIncomeCategory.SALARY,
        comment="Monthly salary",
    )


@pytest.fixture
def sample_expense_transaction() -> Transaction:
    return Transaction(
        id=2,
        amount=150.00,
        date=datetime(2026, 1, 20, 14, 30, 0, tzinfo=timezone.utc),
        type=TransactionType.EXPENSE,
        category=TransactionExpenseCategory.NEED,
        comment="Groceries",
    )


@pytest.fixture
def sample_transactions() -> List[Transaction]:
    return [
        Transaction(
            id=0,
            amount=19.99,
            date=datetime(2026, 3, 2, 20, 50, 32, tzinfo=timezone.utc),
            type=TransactionType.INCOME,
            category=TransactionIncomeCategory.SALARY,
            comment="Test Transaction",
        ),
        Transaction(
            id=1,
            amount=9.99,
            date=datetime(2026, 2, 2, 20, 50, 32, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            category=TransactionExpenseCategory.NEED,
            comment=None,
        ),
    ]
