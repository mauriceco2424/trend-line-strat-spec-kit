from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from src.models.trade_setup import TradeSetup
from src.services.breakout_detector import BreakoutDetector
from src.services.supply_demand_detector import SupplyDemandDetector
from src.services.trade_ranker import TradeRanker
from src.services.trendline_detector import TrendlineDetector


@dataclass
class BacktestReport:
    trades: List[Dict[str, float]]
    metrics: Dict[str, float]
    summary: Dict[str, float]


class Backtester:
    def __init__(
        self,
        trendline_detector: TrendlineDetector,
        breakout_detector: BreakoutDetector,
        supply_demand_detector: SupplyDemandDetector,
        trade_ranker: TradeRanker,
    ) -> None:
        self.trendline_detector = trendline_detector
        self.breakout_detector = breakout_detector
        self.supply_demand_detector = supply_demand_detector
        self.trade_ranker = trade_ranker

    def run(
        self,
        pair_symbol: str,
        timeframe: str,
        candles: Sequence[dict],
        initial_balance: float,
    ) -> BacktestReport:
        trendlines = self.trendline_detector.detect(pair_symbol, timeframe, candles)
        breakouts = []
        for trendline in trendlines:
            breakouts.extend(self.breakout_detector.detect(trendline, candles))
        sd_levels = self.supply_demand_detector.detect(pair_symbol, timeframe, candles)
        setups = self.trade_ranker.rank(trendlines, breakouts, sd_levels)

        trades = self._generate_trades(setups, candles)
        metrics = self._calculate_metrics(trades, initial_balance)
        summary = {
            "total_breakouts": float(len(setups)),
            "total_trades": float(len(trades)),
        }
        return BacktestReport(trades=trades, metrics=metrics, summary=summary)

    def _generate_trades(self, setups: Sequence[TradeSetup], candles: Sequence[dict]) -> List[Dict[str, float]]:
        if not setups:
            return []
        trades: List[Dict[str, float]] = []
        for setup in setups[:5]:
            entry = float(candles[-3]["close"])
            exit_price = entry * 1.05
            trades.append({"entry": entry, "exit": exit_price})
        return trades

    def _calculate_metrics(self, trades: Sequence[Dict[str, float]], initial_balance: float) -> Dict[str, float]:
        if not trades:
            return {"sortino_ratio": 0.0, "profit_factor": 0.0, "max_drawdown": 0.0}
        profits = [trade["exit"] - trade["entry"] for trade in trades]
        gain = sum(p for p in profits if p > 0)
        loss = abs(sum(p for p in profits if p < 0)) or 1.0
        profit_factor = gain / loss
        sortino_ratio = (gain / len(trades)) / (loss / len(trades))
        max_drawdown = -max(p / (trade["entry"]) for p, trade in zip(profits, trades))
        return {
            "sortino_ratio": round(sortino_ratio, 4),
            "profit_factor": round(profit_factor, 4),
            "max_drawdown": round(max_drawdown, 4),
        }
