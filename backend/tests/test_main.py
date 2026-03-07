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


class TestGetTransactionsPagination:
    def _create_transaction_via_api(self, client, amount: float, index: int):
        payload = {
            "amount": amount,
            "date": f"2026-01-{1 + index:02d}T12:00:00Z",
            "type": "expense",
            "category": "need",
            "comment": f"Transaction {index + 1}",
        }
        response = client.post("/transactions/", json=payload)
        assert response.status_code == 201

    def test_get_transactions_limit_only(self, client_with_data):
        for i in range(8):
            self._create_transaction_via_api(client_with_data, 10.00 + i, i)
        response = client_with_data.get("/transactions/?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_transactions_page_and_limit(self, client_with_data):
        for i in range(8):
            self._create_transaction_via_api(client_with_data, 10.00 + i, i)
        response = client_with_data.get("/transactions/?page=2&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_transactions_first_page(self, client_with_data):
        for i in range(8):
            self._create_transaction_via_api(client_with_data, 10.00 + i, i)
        response = client_with_data.get("/transactions/?page=1&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_transactions_last_page(self, client_with_data):
        for i in range(10):
            self._create_transaction_via_api(client_with_data, 10.00 + i, i)
        response = client_with_data.get("/transactions/?page=2&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_get_transactions_page_without_limit(self, client_with_data):
        response = client_with_data.get("/transactions/?page=2")
        assert response.status_code == 422
        assert "limit" in response.json()["detail"].lower()

    def test_get_transactions_limit_exceeds_max(self, client_with_data):
        response = client_with_data.get("/transactions/?limit=51")
        assert response.status_code == 422

    def test_get_transactions_page_less_than_one(self, client_with_data):
        response = client_with_data.get("/transactions/?page=0&limit=10")
        assert response.status_code == 422

    def test_get_transactions_page_beyond_results(self, client_with_data):
        for i in range(3):
            self._create_transaction_via_api(client_with_data, 10.00 + i, i)
        response = client_with_data.get("/transactions/?page=5&limit=10")
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


class TestEditTransaction:
    def test_patch_update_amount(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/1",
            json={"amount": 7500.00, "type": "income", "category": "salary"},
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["amount"])) == Decimal("7500.00")

    def test_patch_update_comment(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/1",
            json={"comment": "Updated comment", "type": "income", "category": "salary"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["comment"] == "Updated comment"

    def test_patch_update_category_same_type(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/1",
            json={"type": "income", "category": "other"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "other"

    def test_patch_update_type_and_category(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/2",
            json={"type": "income", "category": "salary"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "income"
        assert data["category"] == "salary"

    def test_patch_update_multiple_fields(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/1",
            json={
                "amount": 100.00,
                "comment": "New comment",
                "type": "income",
                "category": "other",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["amount"])) == Decimal("100.00")
        assert data["comment"] == "New comment"
        assert data["category"] == "other"

    def test_patch_update_date(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/1",
            json={
                "date": "2026-06-15T10:00:00Z",
                "type": "income",
                "category": "salary",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "2026-06-15" in data["date"]

    def test_patch_not_found(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/999",
            json={"amount": 100.00, "type": "income", "category": "salary"},
        )
        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]

    def test_patch_invalid_type(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/1",
            json={"type": "invalid", "category": "salary"},
        )
        assert response.status_code == 422

    def test_patch_invalid_category(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/1",
            json={"type": "income", "category": "invalid"},
        )
        assert response.status_code == 422

    def test_patch_invalid_type_category_combo(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/1",
            json={"type": "expense", "category": "salary"},
        )
        assert response.status_code == 422

    def test_patch_negative_amount(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/1",
            json={"amount": -100.00, "type": "income", "category": "salary"},
        )
        assert response.status_code == 422

    def test_patch_missing_type(self, client_with_data):
        response = client_with_data.patch(
            "/transactions/1", json={"category": "salary"}
        )
        assert response.status_code == 422

    def test_patch_missing_category(self, client_with_data):
        response = client_with_data.patch("/transactions/1", json={"type": "income"})
        assert response.status_code == 422


class TestDeleteTransaction:
    def test_delete_existing_transaction(self, client_with_data):
        response = client_with_data.delete("/transactions/1")
        assert response.status_code == 204
        assert response.text == ""

    def test_delete_then_get_returns_404(self, client_with_data):
        client_with_data.delete("/transactions/1")
        response = client_with_data.get("/transactions/1")
        assert response.status_code == 404

    def test_delete_nonexistent_transaction(self, client_with_data):
        response = client_with_data.delete("/transactions/999")
        assert response.status_code == 404

    def test_delete_updates_list(self, client_with_data):
        client_with_data.delete("/transactions/1")
        response = client_with_data.get("/transactions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 2

    def test_delete_all_transactions(self, client_with_data):
        client_with_data.delete("/transactions/1")
        client_with_data.delete("/transactions/2")
        response = client_with_data.get("/transactions/")
        assert response.status_code == 404
