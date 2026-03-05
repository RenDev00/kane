from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from model.transaction import (
    Transaction,
    TransactionExpenseCategory,
    TransactionIncomeCategory,
    TransactionType,
)


class TestTransactionType:
    def test_transaction_type_enum_values(self):
        assert TransactionType.INCOME.value == "income"
        assert TransactionType.EXPENSE.value == "expense"

    def test_transaction_type_from_string(self):
        assert TransactionType["INCOME"] == TransactionType.INCOME
        assert TransactionType["EXPENSE"] == TransactionType.EXPENSE


class TestTransactionExpenseCategory:
    def test_expense_category_enum_values(self):
        assert TransactionExpenseCategory.NEED.value == "need"
        assert TransactionExpenseCategory.WANT.value == "want"
        assert TransactionExpenseCategory.SAVING.value == "saving"


class TestTransactionIncomeCategory:
    def test_income_category_enum_values(self):
        assert TransactionIncomeCategory.SALARY.value == "salary"
        assert TransactionIncomeCategory.OTHER.value == "other"


class TestTransactionCreation:
    def test_create_income_transaction_with_all_fields(self, sample_income_transaction):
        assert sample_income_transaction.id == 1
        assert sample_income_transaction.amount == 5000.00
        assert sample_income_transaction.type == TransactionType.INCOME
        assert sample_income_transaction.category == TransactionIncomeCategory.SALARY
        assert sample_income_transaction.comment == "Monthly salary"

    def test_create_expense_transaction_with_all_fields(
        self, sample_expense_transaction
    ):
        assert sample_expense_transaction.id == 2
        assert sample_expense_transaction.amount == 150.00
        assert sample_expense_transaction.type == TransactionType.EXPENSE
        assert sample_expense_transaction.category == TransactionExpenseCategory.NEED
        assert sample_expense_transaction.comment == "Groceries"

    def test_create_transaction_with_minimal_fields(self):
        transaction = Transaction(
            id=3,
            amount=100.00,
            date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            category=TransactionExpenseCategory.WANT,
        )
        assert transaction.comment is None

    def test_transaction_id_is_frozen(self):
        with pytest.raises(ValidationError):
            Transaction(
                id=1,
                amount=100.00,
                date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                category=TransactionExpenseCategory.NEED,
            ).id = 999


class TestDateValidation:
    def test_date_with_aware_datetime_preserved(self):
        dt = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        transaction = Transaction(
            id=1,
            amount=100.00,
            date=dt,
            type=TransactionType.EXPENSE,
            category=TransactionExpenseCategory.NEED,
        )
        assert transaction.date == dt


class TestTypeValidation:
    def test_type_from_string_uppercase(self):
        transaction = Transaction(
            id=1,
            amount=100.00,
            date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            type="EXPENSE",
            category=TransactionExpenseCategory.NEED,
        )
        assert transaction.type == TransactionType.EXPENSE

    def test_type_from_string_lowercase(self):
        transaction = Transaction(
            id=1,
            amount=100.00,
            date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            type="income",
            category=TransactionIncomeCategory.SALARY,
        )
        assert transaction.type == TransactionType.INCOME

    def test_type_from_string_mixed_case(self):
        transaction = Transaction(
            id=1,
            amount=100.00,
            date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            type="InCoMe",
            category=TransactionIncomeCategory.OTHER,
        )
        assert transaction.type == TransactionType.INCOME

    def test_type_from_enum_unchanged(self):
        transaction = Transaction(
            id=1,
            amount=100.00,
            date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            category=TransactionExpenseCategory.SAVING,
        )
        assert transaction.type == TransactionType.EXPENSE

    def test_type_invalid_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            Transaction(
                id=1,
                amount=100.00,
                date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                type="INVALID",
                category=TransactionExpenseCategory.NEED,
            )
        assert "Invalid transaction type" in str(exc_info.value)


class TestCategoryValidation:
    def test_expense_category_from_string(self):
        transaction = Transaction(
            id=1,
            amount=100.00,
            date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            category="need",
        )
        assert transaction.category == TransactionExpenseCategory.NEED

    def test_income_category_from_string(self):
        transaction = Transaction(
            id=1,
            amount=100.00,
            date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            type=TransactionType.INCOME,
            category="salary",
        )
        assert transaction.category == TransactionIncomeCategory.SALARY

    def test_category_from_enum_unchanged(self):
        transaction = Transaction(
            id=1,
            amount=100.00,
            date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            category=TransactionExpenseCategory.WANT,
        )
        assert transaction.category == TransactionExpenseCategory.WANT

    def test_category_invalid_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            Transaction(
                id=1,
                amount=100.00,
                date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                category="INVALID",
            )
        assert "Invalid transaction category" in str(exc_info.value)


class TestCategoryTypeCompatibility:
    def test_expense_with_expense_category_valid(self):
        transaction = Transaction(
            id=1,
            amount=100.00,
            date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            category=TransactionExpenseCategory.NEED,
        )
        assert transaction.category == TransactionExpenseCategory.NEED

    def test_income_with_income_category_valid(self):
        transaction = Transaction(
            id=1,
            amount=100.00,
            date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            type=TransactionType.INCOME,
            category=TransactionIncomeCategory.SALARY,
        )
        assert transaction.category == TransactionIncomeCategory.SALARY

    def test_expense_with_income_category_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            Transaction(
                id=1,
                amount=100.00,
                date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                category=TransactionIncomeCategory.SALARY,
            )
        assert "cannot have category=SALARY" in str(exc_info.value)

    def test_income_with_expense_category_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            Transaction(
                id=1,
                amount=100.00,
                date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                category=TransactionExpenseCategory.WANT,
            )
        assert "cannot have category=WANT" in str(exc_info.value)


class TestTransactionSerialization:
    def test_model_dump(self, sample_income_transaction):
        data = sample_income_transaction.model_dump()
        assert data["id"] == 1
        assert data["amount"] == 5000.00
        assert data["type"] == TransactionType.INCOME
        assert data["category"] == TransactionIncomeCategory.SALARY

    def test_model_dump_json(self, sample_income_transaction):
        json_data = sample_income_transaction.model_dump_json()
        assert '"id":1' in json_data
        assert '"amount":5000.0' in json_data

    def test_model_validate(self):
        data = {
            "id": 1,
            "amount": 100.00,
            "date": "2026-01-01T12:00:00Z",
            "type": "EXPENSE",
            "category": "NEED",
            "comment": "Test",
        }
        transaction = Transaction.model_validate(data)
        assert transaction.id == 1
        assert transaction.amount == 100.00
