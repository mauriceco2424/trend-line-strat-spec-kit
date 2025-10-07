import pytest

from src.services.backtester import Backtester
from src.services.breakout_detector import BreakoutDetector
from src.services.supply_demand_detector import SupplyDemandDetector
from src.services.trade_ranker import TradeRanker
from src.services.trendline_detector import TrendlineDetector


@pytest.fixture
def candles():
    base = []
    for idx in range(90):
        base.append(
            {
                "timestamp": f"2024-09-01T{idx:02d}:00:00Z",
                "open": 1800 + idx * 5,
                "high": 1805 + idx * 5,
                "low": 1795 + idx * 5,
                "close": 1802 + idx * 5,
                "volume": 2000 + idx * 25,
            }
        )
    for idx in range(10):
        base.append(
            {
                "timestamp": f"2024-11-01T{idx:02d}:00:00Z",
                "open": 2250 + idx * 15,
                "high": 2300 + idx * 15,
                "low": 2200 + idx * 15,
                "close": 2280 + idx * 15,
                "volume": 5000 + idx * 200,
            }
        )
    return base


def test_backtester_generates_metrics(candles):
    trendline_detector = TrendlineDetector()
    breakout_detector = BreakoutDetector()
    supply_demand_detector = SupplyDemandDetector()
    ranker = TradeRanker()

    backtester = Backtester(
        trendline_detector=trendline_detector,
        breakout_detector=breakout_detector,
        supply_demand_detector=supply_demand_detector,
        trade_ranker=ranker,
    )

    report = backtester.run(
        pair_symbol="ETHUSDT",
        timeframe="4h",
        candles=candles,
        initial_balance=10000.0,
    )

    assert "sortino_ratio" in report.metrics
    assert "profit_factor" in report.metrics
    assert "max_drawdown" in report.metrics
    assert report.summary["total_breakouts"] >= len(report.trades)
