import pytest

from src.services.breakout_detector import BreakoutDetector
from src.services.supply_demand_detector import SupplyDemandDetector
from src.services.trade_ranker import TradeRanker
from src.services.trendline_detector import TrendlineDetector


@pytest.fixture
def candles():
    base_price = 1800.0
    data = []
    for idx in range(75):
        touches = idx in {12, 33, 48}
        low = base_price + idx * 6 - (25 if touches else 8)
        close = base_price + idx * 6 + (15 if touches else 9)
        data.append(
            {
                "timestamp": f"2024-09-01T{idx:02d}:00:00Z",
                "open": close - 4,
                "high": close + 8,
                "low": low,
                "close": close,
                "volume": 1500 + idx * 40,
            }
        )
    return data


@pytest.fixture
def breakout_series(candles):
    extra = []
    base_close = candles[-1]["close"]
    base_ts = candles[-1]["timestamp"]
    for idx in range(1, 6):
        close = base_close + idx * 20
        extra.append(
            {
                "timestamp": f"2024-10-01T{idx:02d}:00:00Z",
                "open": close - 10,
                "high": close + 30,
                "low": close - 25,
                "close": close,
                "volume": 3000 + idx * 300,
            }
        )
    return [*candles, *extra]


def test_trade_ranker_produces_ordered_setups(candles, breakout_series):
    trendlines = TrendlineDetector().detect("ETHUSDT", "4h", candles)
    breakouts = BreakoutDetector().detect(trendlines[0], breakout_series)
    sd_levels = SupplyDemandDetector().detect("ETHUSDT", "4h", candles)

    ranker = TradeRanker()
    setups = ranker.rank(trendlines, breakouts, sd_levels)
    assert setups
    assert setups[0].confidence_score >= setups[-1].confidence_score


def test_trade_ranker_labels_a_plus(candles, breakout_series):
    trendlines = TrendlineDetector().detect("ETHUSDT", "4h", candles)
    breakouts = BreakoutDetector().detect(trendlines[0], breakout_series)
    sd_levels = SupplyDemandDetector().detect("ETHUSDT", "4h", candles)

    setup = TradeRanker().rank(trendlines, breakouts, sd_levels)[0]
    assert setup.a_plus is True
