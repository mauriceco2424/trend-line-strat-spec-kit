import pytest
from jsonschema import Draft202012Validator

from src.contracts.schemas import load_schema


@pytest.fixture(scope="module")
def schema() -> dict:
    return load_schema("price-data-api")


def test_price_data_schema_requires_required_fields(schema: dict) -> None:
    validator = Draft202012Validator(schema)
    with pytest.raises(Exception):
        validator.validate({})


def test_price_data_schema_allows_valid_candle_payload(schema: dict) -> None:
    validator = Draft202012Validator(schema)
    payload = {
        "symbol": "BTCUSDT",
        "timeframe": "4h",
        "metadata": {
            "generated_at": "2024-10-07T12:00:00Z",
            "source": "binance",
            "bars": 120,
        },
        "candles": [
            {
                "timestamp": "2024-10-07T08:00:00Z",
                "open": 50000.0,
                "high": 50500.0,
                "low": 49800.0,
                "close": 50400.0,
                "volume": 1234.56,
            }
            for _ in range(60)
        ],
    }
    validator.validate(payload)
