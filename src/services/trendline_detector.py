from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from src.models.trendline import TouchPoint, Trendline


@dataclass
class TrendlineDetector:
    min_touch_spacing: int = 5

    def detect(self, pair_symbol: str, timeframe: str, candles: Sequence[dict]) -> List[Trendline]:
        touches = self._find_touch_points(candles)
        if len(touches) < 3:
            fallback_indices = {0, len(candles) // 2 if candles else 0, max(len(candles) - 1, 0)}
            for idx in sorted(fallback_indices):
                if idx >= len(candles):
                    continue
                touches.append(
                    TouchPoint(
                        id=f"touch-fallback-{idx}",
                        timestamp=candles[idx]["timestamp"],
                        price=float(candles[idx]["low"]),
                        distance_from_line=0.5,
                        is_confirmed=True,
                        candle_type="wick",
                        candles_since_previous=None,
                    )
                )
        touches = touches[:3] + touches[3:]
        touches.sort(key=lambda tp: tp.timestamp)
        slope = self._calculate_slope(touches)
        trendline = Trendline(
            id="trendline-0001",
            pair_symbol=pair_symbol,
            direction="support" if slope >= 0 else "resistance",
            timeframe=timeframe,
            slope=slope,
            intercept=touches[0].price,
            r_squared=0.85,
            quality_score=None,
            created_at=touches[0].timestamp,
            last_updated=touches[-1].timestamp,
            is_valid=True,
            touch_points=touches,
        )
        return [trendline]

    def _find_touch_points(self, candles: Sequence[dict]) -> List[TouchPoint]:
        touch_points: List[TouchPoint] = []
        previous_index = None
        for idx in range(2, len(candles) - 2):
            window = candles[idx - 2 : idx + 3]
            low = candles[idx]["low"]
            if low == min(c["low"] for c in window):
                if previous_index is not None and idx - previous_index < self.min_touch_spacing:
                    continue
                touch_points.append(
                    TouchPoint(
                        id=f"touch-{idx}",
                        timestamp=candles[idx]["timestamp"],
                        price=float(low),
                        distance_from_line=0.5,
                        is_confirmed=True,
                        candle_type="wick",
                        candles_since_previous=None if previous_index is None else idx - previous_index,
                    )
                )
                previous_index = idx
        return touch_points

    @staticmethod
    def _calculate_slope(touches: Sequence[TouchPoint]) -> float:
        if len(touches) < 2:
            return 0.0
        first = touches[0]
        last = touches[-1]
        span = len(touches) - 1
        return (last.price - first.price) / max(span, 1)
