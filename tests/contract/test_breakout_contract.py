import pytest
from jsonschema import Draft202012Validator

from src.contracts.schemas import load_schema


def breakout_payload(stage: int) -> dict:
    return {
        "trendline_id": "00000000-0000-0000-0000-000000001111",
        "breakouts": [
            {
                "id": "00000000-0000-0000-0000-000000002222",
                "direction": "upward",
                "timestamp": "2024-10-07T12:00:00Z",
                "price": 50500.0,
                "confirmation_stage": stage,
                "volume": 1500.0,
                "volume_average": 900.0,
                "stages": {
                    "initial_break": {
                        "timestamp": "2024-10-07T08:00:00Z",
                        "price": 50050.0,
                        "close_above_line": True,
                    },
                    "retest": {
                        "timestamp": "2024-10-07T10:00:00Z",
                        "price": 50000.0,
                    }
                    if stage >= 2
                    else None,
                    "rejection": {
                        "timestamp": "2024-10-07T11:00:00Z",
                        "price": 50450.0,
                        "magnitude_pct": 1.1,
                    }
                    if stage == 3
                    else None,
                },
                "higher_timeframe_alignment": {
                    "timeframes": ["daily", "weekly"],
                    "is_confirmed": True,
                },
            }
        ],
    }


@pytest.fixture(scope="module")
def schema() -> dict:
    return load_schema("breakout-detection")


def test_breakout_schema_rejects_invalid_stage(schema: dict) -> None:
    validator = Draft202012Validator(schema)
    data = breakout_payload(stage=4)
    with pytest.raises(Exception):
        validator.validate(data)


def test_breakout_schema_accepts_three_stage_payload(schema: dict) -> None:
    validator = Draft202012Validator(schema)
    validator.validate(breakout_payload(stage=3))
