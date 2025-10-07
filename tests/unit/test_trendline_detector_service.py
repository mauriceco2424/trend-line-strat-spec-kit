import pytest

from src.models.trendline import Trendline
from src.services.trendline_detector import TrendlineDetector


@pytest.fixture
def candles():
    base_price = 1800.0
    return [
        {
            "timestamp": f"2024-09-{day:02d}T00:00:00Z",
            "open": base_price + i * 5,
            "high": base_price + i * 5 + 10,
            "low": base_price + i * 5 - (10 if day in {5, 15, 25} else 4),
            "close": base_price + i * 5 + 5,
            "volume": 2000 + i * 50,
        }
        for i, day in enumerate(range(1, 31))
    ]


def test_trendline_detector_returns_quality_scored_trendlines(candles):
    detector = TrendlineDetector()
    trendlines = detector.detect("ETHUSDT", "4h", candles)
    assert trendlines
    assert all(isinstance(t, Trendline) for t in trendlines)
    assert all(0 <= t.quality_score <= 100 for t in trendlines)


def test_trendline_detector_respects_touch_distribution(candles):
    detector = TrendlineDetector(min_touch_spacing=5)
    trendlines = detector.detect("ETHUSDT", "4h", candles)
    first = trendlines[0]
    assert first.touch_point_count >= 3
