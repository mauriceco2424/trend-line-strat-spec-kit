import pytest
from jsonschema import Draft202012Validator

from src.contracts.schemas import load_schema


def ranking_payload(a_plus: bool = True) -> dict:
    return {
        "generated_at": "2024-10-07T12:00:00Z",
        "setups": [
            {
                "id": "00000000-0000-0000-0000-000000003333",
                "trendline_id": "00000000-0000-0000-0000-000000001111",
                "breakout_id": "00000000-0000-0000-0000-000000002222",
                "timeframe": "4h",
                "confidence_score": 88.0,
                "quality_score": 85.0,
                "confluence_strength": 93.0,
                "a_plus": a_plus,
                "supply_demand_alignment": {
                    "is_aligned": True,
                    "distance_pct": 1.2,
                    "level_ids": [
                        "00000000-0000-0000-0000-000000004444"
                    ],
                },
                "confirmation_factors": [
                    "3+ touches",
                    "SD aligned",
                    "HTF aligned",
                    "Volume spike"
                ],
                "rank": 1,
            }
        ],
    }


@pytest.fixture(scope="module")
def schema() -> dict:
    return load_schema("trade-ranking")


def test_trade_ranking_schema_requires_alignment_details(schema: dict) -> None:
    validator = Draft202012Validator(schema)
    payload = ranking_payload()
    payload["setups"][0]["supply_demand_alignment"].pop("level_ids")
    with pytest.raises(Exception):
        validator.validate(payload)


def test_trade_ranking_schema_accepts_valid_setup(schema: dict) -> None:
    validator = Draft202012Validator(schema)
    validator.validate(ranking_payload())
