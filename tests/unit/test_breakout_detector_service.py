import pytest

from src.services.breakout_detector import BreakoutDetector
from src.services.trendline_detector import TrendlineDetector


@pytest.fixture
def candles():
    base_price = 1820.0
    data = []
    for idx in range(70):
        touch = idx in {14, 32, 51}
        low = base_price + idx * 6 - (18 if touch else 6)
        close = base_price + idx * 6 + (12 if touch else 8)
        data.append(
            {
                "timestamp": f"2024-09-01T{idx:02d}:00:00Z",
                "open": close - 5,
                "high": close + 12,
                "low": low,
                "close": close,
                "volume": 1600 + idx * 35,
            }
        )
    return data


@pytest.fixture
def breakout_extension():
    base_ts = "2024-10-01T00:00:00Z"
    template = []
    for idx in range(5):
        template.append(
            {
                "timestamp": f"2024-10-01T{idx:02d}:00:00Z",
                "open": 1950 + idx * 15,
                "high": 1980 + idx * 20,
                "low": 1900 + idx * 10,
                "close": 1970 + idx * 25,
                "volume": 4000 + idx * 450,
            }
        )
    return template


def test_breakout_detector_three_stage_confirmation(candles, breakout_extension):
    trendline = TrendlineDetector().detect("ETHUSDT", "4h", candles)[0]
    detector = BreakoutDetector(retest_window=5)
    breakouts = detector.detect(trendline, [*candles, *breakout_extension])
    assert any(event.confirmation_stage == 3 for event in breakouts)


def test_breakout_detector_flags_volume_spike(candles, breakout_extension):
    trendline = TrendlineDetector().detect("ETHUSDT", "4h", candles)[0]
    detector = BreakoutDetector()
    event = detector.detect(trendline, [*candles, *breakout_extension])[0]
    assert event.volume > event.volume_average
