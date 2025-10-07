from __future__ import annotations

from dataclasses import dataclass, field
from statistics import pstdev
from typing import List, Optional

from src.lib.timeframe import Timeframe, weight_for_timeframe
from src.lib.validators import (
    _normalize_timestamp,
    ensure_distance_tolerance,
    ensure_timestamp_order,
    ensure_touch_spacing,
)


@dataclass(frozen=True)
class TouchPoint:
    id: str
    timestamp: str
    price: float
    distance_from_line: float
    is_confirmed: bool
    candle_type: str
    candles_since_previous: Optional[int] = None


@dataclass
class Trendline:
    id: str
    pair_symbol: str
    direction: str
    timeframe: str
    slope: float
    intercept: float
    r_squared: float
    quality_score: Optional[float]
    created_at: str
    last_updated: str
    is_valid: bool
    touch_points: List[TouchPoint] = field(default_factory=list)
    touch_distribution_score: Optional[float] = None
    age_days: Optional[int] = None

    def __post_init__(self) -> None:
        if len(self.touch_points) < 3:
            raise ValueError("Trendline requires at least three touch points")
        self._validate_touch_points()
        if self.quality_score is None:
            self.quality_score = self._calculate_quality_score()
        if self.touch_distribution_score is None:
            self.touch_distribution_score = self._calculate_distribution_score()
        if self.age_days is None:
            created = _normalize_timestamp(self.created_at)
            updated = _normalize_timestamp(self.last_updated)
            self.age_days = max((updated - created).days, 0)

    def _validate_touch_points(self) -> None:
        prev_ts = None
        prev_idx = None
        for idx, tp in enumerate(self.touch_points):
            ensure_distance_tolerance(tp.distance_from_line, 1.0)
            if prev_ts is not None:
                ensure_timestamp_order(prev_ts, tp.timestamp)
            if prev_idx is not None and tp.candles_since_previous is not None:
                ensure_touch_spacing(prev_idx, prev_idx + tp.candles_since_previous, 3)
            prev_ts = tp.timestamp
            prev_idx = idx

    def _calculate_distribution_score(self) -> float:
        timestamps = [_normalize_timestamp(tp.timestamp).timestamp() for tp in self.touch_points]
        if len(set(timestamps)) <= 1:
            return 0.0
        spread = pstdev(timestamps)
        normalized = min(spread / (24 * 60 * 60 * 10), 1.0)
        return round(normalized * 100, 2)

    def _calculate_quality_score(self) -> float:
        touch_factor = min(self.touch_point_count / 3.0, 2.0)
        timeframe_weight = weight_for_timeframe(Timeframe.from_str(self.timeframe)) / weight_for_timeframe(Timeframe.WEEKLY)
        distribution = (self._calculate_distribution_score() or 0) / 100
        r_component = self.r_squared
        slope_component = min(abs(self.slope) / 5.0, 1.0)
        score = (
            40 * touch_factor
            + 25 * timeframe_weight
            + 20 * distribution
            + 10 * r_component
            + 5 * slope_component
        )
        return round(min(score, 100.0), 2)

    @property
    def touch_point_count(self) -> int:
        return len(self.touch_points)

    def mark_broken(self) -> None:
        self.is_valid = False

    def revalidate(self) -> None:
        self.is_valid = True
