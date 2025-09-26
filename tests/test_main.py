import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from datetime import date

from app.main import app
from app.models import Market, Commodity, Price
from app.database import get_db
from fastapi import HTTPException

# -----------------------------
# Sample mock data
# -----------------------------
mock_markets = [
    Market(
        market_id=1,
        market_name="Test Market",
        admin1="X",
        admin2="Y",
        country="AFG",
        latitude=0.0,
        longitude=0.0,
    )
]

mock_commodities = [
    Commodity(
        commodity_id=1,
        commodity_name="Wheat",
        category="Cereals",
        unit="KG",
    )
]

mock_prices = [
    Price(
        market_id=1,
        commodity_id=1,
        date=date(2025, 1, 1),
        price=10.0,
        usd_price=0.13,
        priceflag="A",
        pricetype="Retail"
    ),
    Price(
        market_id=1,
        commodity_id=1,
        date=date(2025, 1, 2),
        price=12.0,
        usd_price=0.16,
        priceflag="A",
        pricetype="Retail"
    )
]


# -----------------------------
# Helper mock class
# -----------------------------
class QueryMock(MagicMock):
    def filter(self, *args, **kwargs):
        return self

    def join(self, *args, **kwargs):
        return self

    def all(self):
        if hasattr(self, "_return_data"):
            return self._return_data
        return []

    def first(self):
        if hasattr(self, "_return_data") and self._return_data:
            return self._return_data[0]
        return None


# -----------------------------
# Setup mocked DB session
# -----------------------------
mock_db = MagicMock()


def override_get_db():
    yield mock_db


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# -----------------------------
# Root and health endpoints
# -----------------------------
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "WFP Food Prices API is running!"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is the WFP Food Prices API homepage!"}


# -----------------------------
# Markets endpoints
# -----------------------------
def test_markets_empty():
    q = QueryMock()
    q._return_data = []
    mock_db.query.return_value = q
    response = client.get("/markets")
    assert response.status_code == 200
    assert response.json() == []


def test_markets_with_data():
    q = QueryMock()
    q._return_data = mock_markets
    mock_db.query.return_value = q
    response = client.get("/markets")
    data = response.json()
    assert response.status_code == 200
    assert data[0]["market_name"] == "Test Market"


def test_get_market_found():
    q = QueryMock()
    q._return_data = mock_markets
    mock_db.query.return_value = q
    response = client.get("/markets/1")
    data = response.json()
    assert response.status_code == 200
    assert data["market_name"] == "Test Market"


def test_get_market_not_found():
    q = QueryMock()
    q._return_data = []
    mock_db.query.return_value = q
    response = client.get("/markets/999")
    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == 404


# -----------------------------
# Commodities endpoints
# -----------------------------
def test_commodities_empty():
    q = QueryMock()
    q._return_data = []
    mock_db.query.return_value = q
    response = client.get("/commodities")
    assert response.status_code == 200
    assert response.json() == []


def test_commodities_with_data():
    q = QueryMock()
    q._return_data = mock_commodities
    mock_db.query.return_value = q
    response = client.get("/commodities")
    data = response.json()
    assert response.status_code == 200
    assert data[0]["commodity_name"] == "Wheat"


def test_get_commodity_found():
    q = QueryMock()
    q._return_data = mock_commodities
    mock_db.query.return_value = q
    response = client.get("/commodities/1")
    data = response.json()
    assert response.status_code == 200
    assert data["commodity_name"] == "Wheat"


def test_get_commodity_not_found():
    q = QueryMock()
    q._return_data = []
    mock_db.query.return_value = q
    response = client.get("/commodities/999")
    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == 404


# -----------------------------
# Latest prices endpoint
# -----------------------------
def test_latest_prices():
    q = QueryMock()
    q._return_data = [mock_prices[-1]]  # latest price only
    mock_db.query.return_value = q
    response = client.get("/latest-prices")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["price"] == 12.0


def test_latest_prices_no_data():
    q = QueryMock()
    q._return_data = []
    mock_db.query.return_value = q
    response = client.get("/latest-prices")
    assert response.status_code == 200
    assert response.json() == []


def test_prices_no_matching_filters():
    q = QueryMock()
    q._return_data = []
    mock_db.query.return_value = q
    response = client.get("/prices?market_id=999&commodity_id=999")
    assert response.status_code == 200
    assert response.json() == []


# -----------------------------
# Prices endpoint
# -----------------------------
def test_prices_no_filters():
    q = QueryMock()
    q._return_data = mock_prices
    mock_db.query.return_value = q
    response = client.get("/prices")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2


def test_prices_with_market_filter():
    q = QueryMock()
    q._return_data = [mock_prices[0]]
    mock_db.query.return_value = q
    response = client.get("/prices?market_id=1")
    data = response.json()
    assert response.status_code == 200
    assert data[0]["market_id"] == 1


def test_prices_with_commodity_filter():
    q = QueryMock()
    q._return_data = [mock_prices[1]]
    mock_db.query.return_value = q
    response = client.get("/prices?commodity_id=1")
    data = response.json()
    assert response.status_code == 200
    assert data[0]["commodity_id"] == 1


def test_prices_with_date_range():
    q = QueryMock()
    q._return_data = [mock_prices[0]]
    mock_db.query.return_value = q
    response = client.get("/prices?start_date=2025-01-01&end_date=2025-01-01")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["date"] == "2025-01-01"
