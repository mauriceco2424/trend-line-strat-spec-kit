import pytest

from src.models.supply_demand import SupplyDemandLevel


def test_supply_demand_strength_requires_minimum_touch_count():
    with pytest.raises(ValueError):
        SupplyDemandLevel(
            id="00000000-0000-0000-0000-000000020001",
            pair_symbol="ETHUSDT",
            timeframe="4h",
            price_high=2050.0,
            price_low=2025.0,
            strength_score=None,
            touch_count=2,
            formation_type="demand",
            detected_at="2024-10-07T12:00:00Z",
        )


def test_supply_demand_strength_scoring():
    level = SupplyDemandLevel(
        id="00000000-0000-0000-0000-000000020001",
        pair_symbol="ETHUSDT",
        timeframe="4h",
        price_high=2050.0,
        price_low=2025.0,
        strength_score=None,
        touch_count=4,
        formation_type="demand",
        detected_at="2024-10-07T12:00:00Z",
        last_touched_at="2024-10-07T16:00:00Z",
    )

    assert 0 <= level.strength_score <= 100
    assert level.distance_to_price(2045.0) <= 2.0
