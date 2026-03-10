from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

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


class TestGetMonthlyStats:
    def test_empty_database_returns_zero_filled_months(self, client: TestClient):
        response = client.get("/stats/monthly?months=3&before=2026-04-01T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        assert len(data["months"]) == 3
        for m in data["months"]:
            assert m["total_income"] == "0"
            assert m["total_expense"] == "0"
            assert m["total_need"] == "0"
            assert m["total_want"] == "0"
            assert m["total_saving"] == "0"

    def test_default_returns_six_months(self, client: TestClient):
        with patch(
            "routers.stats.datetime",
        ) as mock_dt:
            mock_dt.now.return_value = datetime(2026, 7, 15, tzinfo=timezone.utc)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            response = client.get("/stats/monthly")
        assert response.status_code == 200
        data = response.json()
        assert len(data["months"]) == 6
        # Mid-month: July is included as a partial month
        assert data["months"][0]["month"] == "2026-02"
        assert data["months"][5]["month"] == "2026-07"

    def test_months_with_data(self, test_db, client: TestClient):
        transactions = [
            TransactionDB(
                amount=Decimal("5000.00"),
                date=datetime(2026, 1, 15, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                income_category=TransactionIncomeCategory.SALARY,
                expense_category=None,
            ),
            TransactionDB(
                amount=Decimal("800.00"),
                date=datetime(2026, 1, 20, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.NEED,
            ),
            TransactionDB(
                amount=Decimal("200.00"),
                date=datetime(2026, 1, 25, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.WANT,
            ),
            TransactionDB(
                amount=Decimal("300.00"),
                date=datetime(2026, 2, 5, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.SAVING,
            ),
        ]
        for t in transactions:
            test_db.add(t)
        test_db.commit()

        response = client.get("/stats/monthly?months=3&before=2026-04-01T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        assert len(data["months"]) == 3

        jan = data["months"][0]
        assert jan["month"] == "2026-01"
        assert jan["total_income"] == "5000.0000000000"
        assert jan["total_expense"] == "1000.0000000000"
        assert jan["total_need"] == "800.0000000000"
        assert jan["total_want"] == "200.0000000000"
        assert jan["total_saving"] == "0"

        feb = data["months"][1]
        assert feb["month"] == "2026-02"
        assert feb["total_income"] == "0"
        assert feb["total_expense"] == "300.0000000000"
        assert feb["total_saving"] == "300.0000000000"

        mar = data["months"][2]
        assert mar["month"] == "2026-03"
        assert mar["total_income"] == "0"
        assert mar["total_expense"] == "0"

    def test_sorted_chronologically(self, test_db, client: TestClient):
        transactions = [
            TransactionDB(
                amount=Decimal("100.00"),
                date=datetime(2026, 3, 1, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                income_category=TransactionIncomeCategory.SALARY,
                expense_category=None,
            ),
            TransactionDB(
                amount=Decimal("200.00"),
                date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                income_category=TransactionIncomeCategory.SALARY,
                expense_category=None,
            ),
        ]
        for t in transactions:
            test_db.add(t)
        test_db.commit()

        response = client.get("/stats/monthly?months=3&before=2026-04-01T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        assert data["months"][0]["month"] == "2026-01"
        assert data["months"][1]["month"] == "2026-02"
        assert data["months"][2]["month"] == "2026-03"

    def test_before_mid_month_includes_partial_month(self, test_db, client: TestClient):
        transactions = [
            TransactionDB(
                amount=Decimal("100.00"),
                date=datetime(2026, 3, 10, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                income_category=TransactionIncomeCategory.SALARY,
                expense_category=None,
            ),
            TransactionDB(
                amount=Decimal("500.00"),
                date=datetime(2026, 3, 20, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                income_category=TransactionIncomeCategory.SALARY,
                expense_category=None,
            ),
        ]
        for t in transactions:
            test_db.add(t)
        test_db.commit()

        response = client.get("/stats/monthly?months=3&before=2026-03-15T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        assert data["months"][-1]["month"] == "2026-03"
        # Only the transaction before the cutoff is included
        assert data["months"][-1]["total_income"] == "100.0000000000"

    def test_before_end_of_month_includes_transactions(
        self, test_db, client: TestClient
    ):
        transactions = [
            TransactionDB(
                amount=Decimal("250.00"),
                date=datetime(2026, 3, 15, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.NEED,
            ),
            TransactionDB(
                amount=Decimal("100.00"),
                date=datetime(2026, 2, 10, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                income_category=TransactionIncomeCategory.SALARY,
                expense_category=None,
            ),
        ]
        for t in transactions:
            test_db.add(t)
        test_db.commit()

        response = client.get(
            "/stats/monthly?months=2&before=2026-03-31T21:59:59.000Z"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["months"]) == 2
        assert data["months"][0]["month"] == "2026-02"
        assert data["months"][0]["total_income"] == "100.0000000000"
        assert data["months"][1]["month"] == "2026-03"
        assert data["months"][1]["total_expense"] == "250.0000000000"
        assert data["months"][1]["total_need"] == "250.0000000000"

    def test_before_first_of_month_excludes_that_month(
        self, test_db, client: TestClient
    ):
        transaction = TransactionDB(
            amount=Decimal("100.00"),
            date=datetime(2026, 3, 10, tzinfo=timezone.utc),
            type=TransactionType.INCOME,
            income_category=TransactionIncomeCategory.SALARY,
            expense_category=None,
        )
        test_db.add(transaction)
        test_db.commit()

        response = client.get("/stats/monthly?months=3&before=2026-03-01T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        months = [m["month"] for m in data["months"]]
        assert "2026-03" not in months
        assert data["months"][-1]["month"] == "2026-02"

    def test_spanning_year_boundary(self, test_db, client: TestClient):
        transactions = [
            TransactionDB(
                amount=Decimal("100.00"),
                date=datetime(2025, 11, 15, tzinfo=timezone.utc),
                type=TransactionType.INCOME,
                income_category=TransactionIncomeCategory.SALARY,
                expense_category=None,
            ),
            TransactionDB(
                amount=Decimal("200.00"),
                date=datetime(2026, 1, 15, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.NEED,
            ),
        ]
        for t in transactions:
            test_db.add(t)
        test_db.commit()

        response = client.get("/stats/monthly?months=6&before=2026-03-01T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        assert len(data["months"]) == 6
        assert data["months"][0]["month"] == "2025-09"
        assert data["months"][5]["month"] == "2026-02"

        nov = next(m for m in data["months"] if m["month"] == "2025-11")
        assert nov["total_income"] == "100.0000000000"

        jan = next(m for m in data["months"] if m["month"] == "2026-01")
        assert jan["total_expense"] == "200.0000000000"
        assert jan["total_need"] == "200.0000000000"

    def test_single_month(self, test_db, client: TestClient):
        transaction = TransactionDB(
            amount=Decimal("500.00"),
            date=datetime(2026, 2, 10, tzinfo=timezone.utc),
            type=TransactionType.INCOME,
            income_category=TransactionIncomeCategory.SALARY,
            expense_category=None,
        )
        test_db.add(transaction)
        test_db.commit()

        response = client.get("/stats/monthly?months=1&before=2026-03-01T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        assert len(data["months"]) == 1
        assert data["months"][0]["month"] == "2026-02"
        assert data["months"][0]["total_income"] == "500.0000000000"

    def test_months_with_no_data_have_zero_values(self, test_db, client: TestClient):
        transaction = TransactionDB(
            amount=Decimal("100.00"),
            date=datetime(2026, 1, 10, tzinfo=timezone.utc),
            type=TransactionType.INCOME,
            income_category=TransactionIncomeCategory.SALARY,
            expense_category=None,
        )
        test_db.add(transaction)
        test_db.commit()

        response = client.get("/stats/monthly?months=3&before=2026-04-01T00:00:00Z")
        assert response.status_code == 200
        data = response.json()

        feb = data["months"][1]
        assert feb["month"] == "2026-02"
        assert feb["total_income"] == "0"
        assert feb["total_expense"] == "0"
        assert feb["total_need"] == "0"
        assert feb["total_want"] == "0"
        assert feb["total_saving"] == "0"

    def test_expense_total_equals_category_sum(self, test_db, client: TestClient):
        transactions = [
            TransactionDB(
                amount=Decimal("400.00"),
                date=datetime(2026, 1, 5, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.NEED,
            ),
            TransactionDB(
                amount=Decimal("200.00"),
                date=datetime(2026, 1, 10, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.WANT,
            ),
            TransactionDB(
                amount=Decimal("100.00"),
                date=datetime(2026, 1, 15, tzinfo=timezone.utc),
                type=TransactionType.EXPENSE,
                income_category=None,
                expense_category=TransactionExpenseCategory.SAVING,
            ),
        ]
        for t in transactions:
            test_db.add(t)
        test_db.commit()

        response = client.get("/stats/monthly?months=1&before=2026-02-01T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        jan = data["months"][0]
        total_expense = Decimal(jan["total_expense"])
        total_need = Decimal(jan["total_need"])
        total_want = Decimal(jan["total_want"])
        total_saving = Decimal(jan["total_saving"])
        assert total_expense == total_need + total_want + total_saving
