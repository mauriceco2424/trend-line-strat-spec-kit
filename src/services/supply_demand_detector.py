from __future__ import annotations

from statistics import mean
from typing import List, Sequence

from src.models.supply_demand import SupplyDemandLevel


class SupplyDemandDetector:
    def __init__(self, distance_threshold_pct: float = 2.0) -> None:
        self.distance_threshold_pct = distance_threshold_pct

    def detect(self, pair_symbol: str, timeframe: str, candles: Sequence[dict]) -> List[SupplyDemandLevel]:
        if not candles:
            return []
        lows = sorted(candles, key=lambda c: c["low"])[:5]
        highs = sorted(candles, key=lambda c: c["high"], reverse=True)[:5]
        demand_level = self._build_level(pair_symbol, timeframe, lows, formation_type="demand")
        supply_level = self._build_level(pair_symbol, timeframe, highs, formation_type="supply")
        return [demand_level, supply_level]

    def _build_level(
        self,
        pair_symbol: str,
        timeframe: str,
        points: Sequence[dict],
        formation_type: str,
    ) -> SupplyDemandLevel:
        if not points:
            raise ValueError("Cannot build level without points")
        if formation_type == "demand":
            base_prices = [float(p["low"]) for p in points]
        else:
            base_prices = [float(p["high"]) for p in points]
        center = mean(base_prices)
        band = max(center * 0.01, 1.0)
        price_low = center - band / 2
        price_high = center + band / 2
        detected_at = points[-1]["timestamp"]
        return SupplyDemandLevel(
            id=f"sd-{formation_type}",
            pair_symbol=pair_symbol,
            timeframe=timeframe,
            price_high=price_high,
            price_low=price_low,
            strength_score=None,
            touch_count=max(len(points), 3),
            formation_type=formation_type,
            detected_at=detected_at,
            last_touched_at=detected_at,
        )
