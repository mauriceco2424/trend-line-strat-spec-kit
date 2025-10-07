import pytest
from jsonschema import Draft202012Validator

from src.contracts.schemas import load_schema


def build_trendline_payload(touch_count: int = 3) -> dict:
    return {
        "pair_symbol": "ETHUSDT",
        "timeframe": "daily",
        "trendlines": [
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "direction": "support",
                "timeframe": "daily",
                "touch_points": [
                    {
                        "id": f"00000000-0000-0000-0000-00000000010{idx}",
                        "timestamp": f"2024-09-0{idx}T00:00:00Z",
                        "price": 1000.0 + idx,
                        "distance_from_line": 0.2,
                        "is_confirmed": True,
                        "candle_type": "wick",
                        "candles_since_previous": idx,
                    }
                    for idx in range(1, touch_count + 1)
                ],
                "slope": 1.5,
                "intercept": 950.0,
                "r_squared": 0.82,
                "quality_score": 78.5,
                "created_at": "2024-09-01T00:00:00Z",
                "last_updated": "2024-10-01T00:00:00Z",
                "is_valid": True,
                "touch_distribution_score": 55.0,
                "age_days": 30,
            }
        ],
    }


@pytest.fixture(scope="module")
def schema() -> dict:
    return load_schema("trendline-detection")


def test_trendline_schema_requires_three_touch_points(schema: dict) -> None:
    validator = Draft202012Validator(schema)
    payload = build_trendline_payload(touch_count=2)
    with pytest.raises(Exception):
        validator.validate(payload)


def test_trendline_schema_accepts_valid_payload(schema: dict) -> None:
    validator = Draft202012Validator(schema)
    payload = build_trendline_payload(touch_count=3)
    validator.validate(payload)
