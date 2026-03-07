from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from database.models import TransactionDB
from model.transaction import (
    TransactionExpenseCategory,
    TransactionIncomeCategory,
    TransactionType,
)


class TestGetNumberOfTransactions:
    def test_empty_database_returns_zero(self, client: TestClient):
        response = client.get("/stats/num_transactions")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 0}

    def test_count_all_transactions(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/num_transactions")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 2}

    def test_filter_by_type_income(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/num_transactions?type=INCOME")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_type_expense(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/num_transactions?type=EXPENSE")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_type_lowercase(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/num_transactions?type=income")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_type_mixed_case(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/num_transactions?type=InCoMe")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_invalid_type(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/num_transactions?type=INVALID")
        assert response.status_code == 422
        assert "invalid transaction type" in response.json()["detail"].lower()

    def test_filter_by_income_category(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/num_transactions?category=SALARY")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_expense_category(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/num_transactions?category=NEED")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_category_lowercase(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/num_transactions?category=salary")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_invalid_category(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/num_transactions?category=INVALID")
        assert response.status_code == 422
        assert "invalid transaction category" in response.json()["detail"].lower()

    def test_filter_by_date_before(self, client_with_data: TestClient):
        before_date = "2026-03-01T00:00:00Z"
        response = client_with_data.get(f"/stats/num_transactions?before={before_date}")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_date_after(self, client_with_data: TestClient):
        after_date = "2026-02-15T00:00:00Z"
        response = client_with_data.get(f"/stats/num_transactions?after={after_date}")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_date_range(self, client_with_data: TestClient):
        before_date = "2026-03-01T00:00:00Z"
        after_date = "2026-02-01T00:00:00Z"
        response = client_with_data.get(
            f"/stats/num_transactions?before={before_date}&after={after_date}"
        )
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_date_no_matches(self, client_with_data: TestClient):
        before_date = "2025-01-01T00:00:00Z"
        response = client_with_data.get(f"/stats/num_transactions?before={before_date}")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 0}

    def test_combined_filters_type_and_category(self, client_with_data: TestClient):
        response = client_with_data.get(
            "/stats/num_transactions?type=INCOME&category=SALARY"
        )
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_combined_filters_no_matches(self, client_with_data: TestClient):
        response = client_with_data.get(
            "/stats/num_transactions?type=INCOME&category=NEED"
        )
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 0}

    def test_all_filters_combined(self, client_with_data: TestClient):
        before_date = "2026-12-31T00:00:00Z"
        after_date = "2026-01-01T00:00:00Z"
        response = client_with_data.get(
            f"/stats/num_transactions?before={before_date}&after={after_date}&type=INCOME&category=SALARY"
        )
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}


class TestGetNumberOfTransactionsEdgeCases:
    def test_multiple_transactions_same_type(self, test_db, client: TestClient):
        for i in range(3):
            transaction = TransactionDB(
                amount=100.00 + i,
                date=datetime(2026, 1, i + 1, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                income_category=TransactionIncomeCategory.SALARY,
                expense_category=None,
            )
            test_db.add(transaction)
        test_db.commit()

        response = client.get("/stats/num_transactions")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 3}

        response = client.get("/stats/num_transactions?type=INCOME")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 3}

    def test_filter_by_expense_category_other(self, test_db, client: TestClient):
        transaction = TransactionDB(
            amount=50.00,
            date=datetime(2026, 1, 15, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            income_category=None,
            expense_category=TransactionExpenseCategory.WANT,
        )
        test_db.add(transaction)
        test_db.commit()

        response = client.get("/stats/num_transactions?category=WANT")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_filter_by_income_category_other(self, test_db, client: TestClient):
        transaction = TransactionDB(
            amount=200.00,
            date=datetime(2026, 1, 15, tzinfo=timezone.utc),
            type=TransactionType.INCOME,
            income_category=TransactionIncomeCategory.OTHER,
            expense_category=None,
        )
        test_db.add(transaction)
        test_db.commit()

        response = client.get("/stats/num_transactions?category=OTHER")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}

    def test_category_filter_returns_zero_for_wrong_type(
        self, test_db, client: TestClient
    ):
        transaction = TransactionDB(
            amount=100.00,
            date=datetime(2026, 1, 15, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            income_category=None,
            expense_category=TransactionExpenseCategory.NEED,
        )
        test_db.add(transaction)
        test_db.commit()

        response = client.get("/stats/num_transactions?category=SALARY")
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 0}

    def test_before_and_after_same_date(self, client_with_data: TestClient):
        date = "2026-02-02T20:50:32Z"
        response = client_with_data.get(
            f"/stats/num_transactions?before={date}&after={date}"
        )
        assert response.status_code == 200
        assert response.json() == {"num_transactions": 1}


class TestGetTotalTransactionAmounts:
    def test_empty_database_returns_zeros(self, client: TestClient):
        response = client.get("/stats/totals")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "total_balance": "0",
            "total_income": "0",
            "total_expense": "0",
            "total_need": "0",
            "total_want": "0",
            "total_saving": "0",
            "total_salary": "0",
            "total_other": "0",
        }

    def test_totals_with_mixed_transactions(self, client_with_data: TestClient):
        response = client_with_data.get("/stats/totals")
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == "19.9900000000"
        assert data["total_expense"] == "9.9900000000"
        assert data["total_balance"] == "10.0000000000"
        assert data["total_salary"] == "19.9900000000"
        assert data["total_need"] == "9.9900000000"
        assert data["total_want"] == "0"
        assert data["total_saving"] == "0"
        assert data["total_other"] == "0"

    def test_totals_filter_by_date_before(self, client_with_data: TestClient):
        before_date = "2026-03-01T00:00:00Z"
        response = client_with_data.get(f"/stats/totals?before={before_date}")
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == "0"
        assert data["total_expense"] == "9.9900000000"
        assert data["total_balance"] == "-9.9900000000"
        assert data["total_need"] == "9.9900000000"
        assert data["total_salary"] == "0"

    def test_totals_filter_by_date_after(self, client_with_data: TestClient):
        after_date = "2026-02-15T00:00:00Z"
        response = client_with_data.get(f"/stats/totals?after={after_date}")
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == "19.9900000000"
        assert data["total_expense"] == "0"
        assert data["total_balance"] == "19.9900000000"
        assert data["total_salary"] == "19.9900000000"
        assert data["total_need"] == "0"

    def test_totals_filter_by_date_range(self, client_with_data: TestClient):
        before_date = "2026-03-01T00:00:00Z"
        after_date = "2026-02-01T00:00:00Z"
        response = client_with_data.get(
            f"/stats/totals?before={before_date}&after={after_date}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == "0"
        assert data["total_expense"] == "9.9900000000"
        assert data["total_balance"] == "-9.9900000000"
        assert data["total_need"] == "9.9900000000"

    def test_totals_with_only_income(self, test_db, client: TestClient):
        transaction = TransactionDB(
            amount=Decimal("1000.00"),
            date=datetime(2026, 1, 15, tzinfo=timezone.utc),
            type=TransactionType.INCOME,
            income_category=TransactionIncomeCategory.SALARY,
            expense_category=None,
        )
        test_db.add(transaction)
        test_db.commit()

        response = client.get("/stats/totals")
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == "1000.0000000000"
        assert data["total_expense"] == "0"
        assert data["total_balance"] == "1000.0000000000"
        assert data["total_salary"] == "1000.0000000000"
        assert data["total_other"] == "0"

    def test_totals_with_only_expense(self, test_db, client: TestClient):
        transaction = TransactionDB(
            amount=Decimal("500.00"),
            date=datetime(2026, 1, 15, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            income_category=None,
            expense_category=TransactionExpenseCategory.WANT,
        )
        test_db.add(transaction)
        test_db.commit()

        response = client.get("/stats/totals")
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == "0"
        assert data["total_expense"] == "500.0000000000"
        assert data["total_balance"] == "-500.0000000000"
        assert data["total_want"] == "500.0000000000"
        assert data["total_need"] == "0"
        assert data["total_saving"] == "0"

    def test_totals_with_multiple_categories(self, test_db, client: TestClient):
        transactions = [
            TransactionDB(
                amount=Decimal("3000.00"),
                date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                income_category=TransactionIncomeCategory.SALARY,
                expense_category=None,
            ),
            TransactionDB(
                amount=Decimal("500.00"),
                date=datetime(2026, 1, 2, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                income_category=TransactionIncomeCategory.OTHER,
                expense_category=None,
            ),
            TransactionDB(
                amount=Decimal("800.00"),
                date=datetime(2026, 1, 3, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.NEED,
            ),
            TransactionDB(
                amount=Decimal("200.00"),
                date=datetime(2026, 1, 4, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.WANT,
            ),
            TransactionDB(
                amount=Decimal("300.00"),
                date=datetime(2026, 1, 5, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.SAVING,
            ),
        ]
        for t in transactions:
            test_db.add(t)
        test_db.commit()

        response = client.get("/stats/totals")
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == "3500.0000000000"
        assert data["total_expense"] == "1300.0000000000"
        assert data["total_balance"] == "2200.0000000000"
        assert data["total_salary"] == "3000.0000000000"
        assert data["total_other"] == "500.0000000000"
        assert data["total_need"] == "800.0000000000"
        assert data["total_want"] == "200.0000000000"
        assert data["total_saving"] == "300.0000000000"

    def test_totals_with_negative_balance(self, test_db, client: TestClient):
        transaction = TransactionDB(
            amount=Decimal("100.00"),
            date=datetime(2026, 1, 15, tzinfo=timezone.utc),
            type=TransactionType.EXPENSE,
            income_category=None,
            expense_category=TransactionExpenseCategory.NEED,
        )
        test_db.add(transaction)
        test_db.commit()

        response = client.get("/stats/totals")
        assert response.status_code == 200
        data = response.json()
        assert data["total_balance"] == "-100.0000000000"

    def test_totals_all_filters_combined(self, client_with_data: TestClient, test_db):
        before_date = "2026-12-31T00:00:00Z"
        after_date = "2026-01-01T00:00:00Z"
        response = client_with_data.get(
            f"/stats/totals?before={before_date}&after={after_date}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_income"] == "19.9900000000"
        assert data["total_expense"] == "9.9900000000"
        assert data["total_balance"] == "10.0000000000"
