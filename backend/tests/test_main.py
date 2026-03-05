class TestGetTransactions:
    def test_get_all_transactions(self, client):
        response = client.get("/transactions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_transactions_filter_by_amount(self, client):
        response = client.get("/transactions/?amount=19.99")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["amount"] == 19.99

    def test_get_transactions_filter_by_type(self, client):
        response = client.get("/transactions/?type=income")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "income"

    def test_get_transactions_filter_by_category(self, client):
        response = client.get("/transactions/?category=need")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "need"

    def test_get_transactions_filter_by_comment(self, client):
        response = client.get("/transactions/?comment=Test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Test" in data[0]["comment"]

    def test_get_transactions_filter_by_comment_case_insensitive(self, client):
        response = client.get("/transactions/?comment=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_transactions_filter_by_before(self, client):
        response = client.get("/transactions/?before=2026-02-15T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_transactions_filter_by_after(self, client):
        response = client.get("/transactions/?after=2026-02-15T00:00:00Z")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_transactions_filter_by_before_and_after(self, client):
        response = client.get(
            "/transactions/?after=2026-01-01T00:00:00Z&before=2026-03-15T00:00:00Z"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_transactions_no_matches(self, client):
        response = client.get("/transactions/?amount=999999")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestGetTransactionById:
    def test_get_transaction_by_id_existing(self, client):
        response = client.get("/transactions/0")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 0

    def test_get_transaction_by_id_second(self, client):
        response = client.get("/transactions/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    def test_get_transaction_by_id_not_found(self, client):
        response = client.get("/transactions/999")
        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"]

    def test_get_transaction_by_id_negative(self, client):
        response = client.get("/transactions/-1")
        assert response.status_code == 404


class TestTransactionSerialization:
    def test_response_contains_all_fields(self, client):
        response = client.get("/transactions/0")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "amount" in data
        assert "date" in data
        assert "type" in data
        assert "category" in data
        assert "comment" in data
