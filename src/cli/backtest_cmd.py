from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from rich.console import Console

from src.cli.detect_cmd import _fetch_candles
from src.services.backtester import Backtester
from src.services.breakout_detector import BreakoutDetector
from src.services.supply_demand_detector import SupplyDemandDetector
from src.services.trade_ranker import TradeRanker
from src.services.trendline_detector import TrendlineDetector

console = Console()


def run_backtest(config_path: Path) -> Dict[str, Any]:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    candles = asyncio.run(_fetch_candles(config))
    backtester = Backtester(
        trendline_detector=TrendlineDetector(),
        breakout_detector=BreakoutDetector(),
        supply_demand_detector=SupplyDemandDetector(),
        trade_ranker=TradeRanker(),
    )
    report = backtester.run(
        pair_symbol=config["pair_symbol"],
        timeframe=config["timeframe"],
        candles=candles,
        initial_balance=float(config.get("initial_balance", 10_000.0)),
    )
    return {
        "trades": report.trades,
        "metrics": report.metrics,
        "summary": report.summary,
    }


def backtest_command(config: Path) -> None:
    result = run_backtest(config)
    console.print_json(data=result)
