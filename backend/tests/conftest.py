from datetime import datetime, timezone
from decimal import Decimal
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import Session, sessionmaker

from database.database import Base, get_db
from database.models import TransactionDB
from main import app
from model.transaction import (
    Transaction,
    TransactionExpenseCategory,
    TransactionIncomeCategory,
    TransactionType,
)


@pytest.fixture(scope="function")
def test_engine():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _create_client_with_test_data(test_db: Session) -> TestClient:
    transactions = [
        TransactionDB(
            amount=Decimal("19.99"),
            date=datetime(2026, 3, 2, 20, 50, 32, tzinfo=timezone.utc),
            type=TransactionType.INCOME,
            income_category=TransactionIncomeCategory.SALARY,
            expense_category=None,
            comment="Test Transaction",
        ),
        TransactionDB(
            amount=Decimal("9.99"),
            date=datetime(2026, 2, 2, 20, 50, 32, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            income_category=None,
            expense_category=TransactionExpenseCategory.NEED,
            comment=None,
        ),
    ]
    for t in transactions:
        test_db.add(t)
    test_db.commit()

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def client(test_db) -> Generator[TestClient]:
    app.dependency_overrides[get_db] = lambda: test_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_data(test_db) -> Generator[TestClient]:
    client = _create_client_with_test_data(test_db)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_income_transaction() -> Transaction:
    return Transaction(
        id=1,
        amount=Decimal("5000.00"),
        date=datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        type=TransactionType.INCOME,
        category=TransactionIncomeCategory.SALARY,
        comment="Monthly salary",
    )


@pytest.fixture
def sample_expense_transaction() -> Transaction:
    return Transaction(
        id=2,
        amount=Decimal("150.00"),
        date=datetime(2026, 1, 20, 14, 30, 0, tzinfo=timezone.utc),
        type=TransactionType.EXPENSE,
        category=TransactionExpenseCategory.NEED,
        comment="Groceries",
    )
