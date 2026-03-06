from decimal import Decimal

import pytest


class TestCreateTransaction:
    def test_create_income_transaction(self, client):
        payload = {
            "amount": 5000.00,
            "date": "2026-01-15T10:00:00Z",
            "type": "income",
            "category": "salary",
            "comment": "Monthly salary",
        }
        response = client.post("/transactions/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert Decimal(str(data["amount"])) == Decimal("5000.00")
        assert data["type"] == "income"
        assert data["category"] == "salary"
        assert data["comment"] == "Monthly salary"
        assert "id" in data

    def test_create_expense_transaction(self, client):
        payload = {
            "amount": 150.00,
            "date": "2026-01-20T14:30:00Z",
            "type": "expense",
            "category": "need",
            "comment": "Groceries",
        }
        response = client.post("/transactions/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert Decimal(str(data["amount"])) == Decimal("150.00")
        assert data["type"] == "expense"
        assert data["category"] == "need"

    def test_create_transaction_without_comment(self, client):
        payload = {
            "amount": 50.00,
            "date": "2026-01-25T12:00:00Z",
            "type": "expense",
            "category": "want",
        }
        response = client.post("/transactions/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["comment"] is None

    @pytest.mark.parametrize(
        "invalid_type",
        ["invalid", "INVALID", "in", "expensee", ""],
    )
    def test_create_transaction_invalid_type(self, client, invalid_type):
        payload = {
            "amount": 100.00,
            "date": "2026-01-01T12:00:00Z",
            "type": invalid_type,
            "category": "need",
        }
        response = client.post("/transactions/", json=payload)
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "invalid_category",
        ["invalid", "INVALID", "neeed", "salaryy", ""],
    )
    def test_create_transaction_invalid_category(self, client, invalid_category):
        payload = {
            "amount": 100.00,
            "date": "2026-01-01T12:00:00Z",
            "type": "expense",
            "category": invalid_category,
        }
        response = client.post("/transactions/", json=payload)
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "amount,expected_status",
        [
            (0, 201),
            (0.01, 201),
            (999999999.99, 201),
            (-1, 422),
            (-100.50, 422),
        ],
    )
    def test_create_transaction_amount_edge_cases(
        self, client, amount, expected_status
    ):
        payload = {
            "amount": amount,
            "date": "2026-01-01T12:00:00Z",
            "type": "expense",
            "category": "need",
        }
        response = client.post("/transactions/", json=payload)
        assert response.status_code == expected_status


class TestGetTransactions:
    def test_get_all_transactions(self, client_with_data):
        response = client_with_data.get("/transactions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_transactions_filter_by_amount(self, client_with_data):
        response = client_with_data.get("/transactions/?amount=19.99")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert Decimal(str(data[0]["amount"])) == Decimal("19.99")

    def test_get_transactions_filter_by_type(self, client_with_data):
        response = client_with_data.get("/transactions/?type=income")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "income"

    def test_get_transactions_filter_by_category(self, client_with_data):
        response = client_with_data.get("/transactions/?category=need")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "need"

    def test_get_transactions_filter_by_comment(self, client_with_data):
        response = client_with_data.get("/transactions/?comment=Test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Test" in data[0]["comment"]

    def test_get_transactions_filter_by_comment_case_insensitive(
        self, client_with_data
    ):
        response = client_with_data.get("/transactions/?comment=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_transactions_filter_by_before(self, client_with_data):
        response = client_with_data.get("/transactions/?before=2026-02-15T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_transactions_filter_by_after(self, client_with_data):
        response = client_with_data.get("/transactions/?after=2026-02-15T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_transactions_filter_by_before_and_after(self, client_with_data):
        response = client_with_data.get(
            "/transactions/?after=2026-01-01T00:00:00Z&before=2026-03-15T00:00:00Z"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.parametrize(
        "url,expected_count",
        [
            ("/transactions/?before=2026-02-02T20:50:32Z", 1),
            ("/transactions/?after=2026-03-02T20:50:32Z", 1),
            ("/transactions/?before=2026-01-01T00:00:00Z", 0),
            ("/transactions/?after=2026-12-31T23:59:59Z", 0),
        ],
    )
    def test_get_transactions_date_boundary_cases(
        self, client_with_data, url, expected_count
    ):
        response = client_with_data.get(url)
        if expected_count == 0:
            assert response.status_code == 404
        else:
            assert response.status_code == 200
            data = response.json()
            assert len(data) == expected_count

    def test_get_transactions_no_matches(self, client_with_data):
        response = client_with_data.get("/transactions/?amount=999999")
        assert response.status_code == 404
        assert "No matching transactions found" in response.json()["detail"]

    def test_get_transactions_empty_database(self, client):
        response = client.get("/transactions/")
        assert response.status_code == 404


class TestGetTransactionById:
    def test_get_transaction_by_id_first(self, client_with_data):
        response = client_with_data.get("/transactions/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    def test_get_transaction_by_id_second(self, client_with_data):
        response = client_with_data.get("/transactions/2")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2

    def test_get_transaction_by_id_not_found(self, client_with_data):
        response = client_with_data.get("/transactions/999")
        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]

    def test_get_transaction_by_id_negative(self, client_with_data):
        response = client_with_data.get("/transactions/-1")
        assert response.status_code == 404


class TestTransactionSerialization:
    def test_response_contains_all_fields(self, client_with_data):
        response = client_with_data.get("/transactions/1")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "amount" in data
        assert "date" in data
        assert "type" in data
        assert "category" in data
        assert "comment" in data

    def test_income_transaction_returns_income_category(self, client_with_data):
        response = client_with_data.get("/transactions/1")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "income"
        assert data["category"] == "salary"

    def test_expense_transaction_returns_expense_category(self, client_with_data):
        response = client_with_data.get("/transactions/2")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "expense"
        assert data["category"] == "need"
