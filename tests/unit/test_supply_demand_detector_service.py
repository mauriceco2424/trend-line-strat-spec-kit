import pytest

from src.services.supply_demand_detector import SupplyDemandDetector


@pytest.fixture
def candles():
    base_price = 1900.0
    data = []
    for idx in range(60):
        is_zone = idx in {10, 18, 34, 47}
        close = base_price + idx * 5 + (20 if is_zone else 5)
        data.append(
            {
                "timestamp": f"2024-09-01T{idx:02d}:00:00Z",
                "open": close - 4,
                "high": close + 8,
                "low": close - (20 if is_zone else 6),
                "close": close,
                "volume": 2000 + idx * 30,
            }
        )
    return data


def test_supply_demand_detector_identifies_zones(candles):
    detector = SupplyDemandDetector(distance_threshold_pct=2.0)
    levels = detector.detect("ETHUSDT", "4h", candles)
    assert levels
    assert any(level.formation_type in {"supply", "demand"} for level in levels)


def test_supply_demand_detector_returns_alignment_candidates(candles):
    detector = SupplyDemandDetector(distance_threshold_pct=2.0)
    levels = detector.detect("ETHUSDT", "4h", candles)
    assert levels
    assert all(level.distance_to_price(level.price_high) <= 2.0 for level in levels)
