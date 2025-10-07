from src.services.backtester import Backtester
from src.services.breakout_detector import BreakoutDetector
from src.services.supply_demand_detector import SupplyDemandDetector
from src.services.trade_ranker import TradeRanker
from src.services.trendline_detector import TrendlineDetector


def test_backtest_flow(backtest_candles) -> None:
    trendline_detector = TrendlineDetector()
    breakout_detector = BreakoutDetector()
    sd_detector = SupplyDemandDetector()
    ranker = TradeRanker()

    backtester = Backtester(
        trendline_detector=trendline_detector,
        breakout_detector=breakout_detector,
        supply_demand_detector=sd_detector,
        trade_ranker=ranker,
    )

    report = backtester.run(
        pair_symbol="ETHUSDT",
        timeframe="4h",
        candles=backtest_candles,
        initial_balance=10000.0,
    )

    assert report.trades, "Backtester should register trades for detected breakouts"
    assert report.metrics["sortino_ratio"] is not None
    assert report.metrics["profit_factor"] is not None
    assert report.metrics["max_drawdown"] <= 0
    assert report.summary["total_breakouts"] >= len(report.trades)
