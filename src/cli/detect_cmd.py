from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from src.services.price_fetcher import PriceFetcher
from src.services.trendline_detector import TrendlineDetector
from src.services.breakout_detector import BreakoutDetector
from src.services.supply_demand_detector import SupplyDemandDetector
from src.services.trade_ranker import TradeRanker

console = Console()


async def _fetch_candles(config: Dict[str, Any]) -> List[dict]:
    fetcher = PriceFetcher(cache_dir=None, universe_size=config.get("universe_size", 50))
    candles = await fetcher.fetch_ohlcv(config["pair_symbol"], config["timeframe"], limit=200)
    await fetcher.close()
    return candles


def run_detection(config_path: Path) -> List[dict]:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    candles = asyncio.run(_fetch_candles(config))
    trendlines = TrendlineDetector().detect(config["pair_symbol"], config["timeframe"], candles)
    breakout_detector = BreakoutDetector()
    breakouts = []
    for trendline in trendlines:
        breakouts.extend(breakout_detector.detect(trendline, candles))
    sd_levels = SupplyDemandDetector().detect(config["pair_symbol"], config["timeframe"], candles)
    setups = TradeRanker().rank(trendlines, breakouts, sd_levels)
    results = [
        {
            "trendline_id": setup.trendline_id,
            "breakout_id": setup.breakout_id,
            "confidence_score": setup.confidence_score,
            "a_plus": setup.a_plus,
        }
        for setup in setups
    ]
    return results


def detect_command(config: Path) -> None:
    setups = run_detection(config)
    if not setups:
        console.print("[yellow]No trade setups detected[/yellow]")
    else:
        console.print_json(data=setups)
