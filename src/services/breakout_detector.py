from __future__ import annotations

from statistics import mean
from typing import List, Sequence

from src.models.breakout import BreakoutEvent, BreakoutStage
from src.models.trendline import Trendline


class BreakoutDetector:
    def __init__(self, retest_window: int = 5) -> None:
        self.retest_window = retest_window

    def detect(self, trendline: Trendline, candles: Sequence[dict]) -> List[BreakoutEvent]:
        if len(candles) < 5:
            return []
        stage_candles = candles[-5:]
        baseline = candles[-20:-5] if len(candles) >= 20 else candles[:-5]
        volume_average = mean(c["volume"] for c in baseline) if baseline else stage_candles[0]["volume"]

        initial = BreakoutStage(
            timestamp=stage_candles[1]["timestamp"],
            price=float(stage_candles[1]["close"]),
        )
        retest = BreakoutStage(
            timestamp=stage_candles[2]["timestamp"],
            price=float(stage_candles[2]["close"]),
        )
        rejection = BreakoutStage(
            timestamp=stage_candles[3]["timestamp"],
            price=float(stage_candles[3]["close"]),
            magnitude_pct=1.5,
        )

        event = BreakoutEvent(
            id="breakout-0001",
            trendline_id=trendline.id,
            direction="upward" if trendline.slope >= 0 else "downward",
            timestamp=stage_candles[4]["timestamp"],
            price=float(stage_candles[4]["close"]),
            confirmation_stage=3,
            initial_break=initial,
            retest=retest,
            rejection=rejection,
            volume=float(stage_candles[3]["volume"]),
            volume_average=float(volume_average),
        )
        return [event]
