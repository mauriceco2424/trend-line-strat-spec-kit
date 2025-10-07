from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.lib.validators import _normalize_timestamp


@dataclass
class SupplyDemandLevel:
    id: str
    pair_symbol: str
    timeframe: str
    price_high: float
    price_low: float
    strength_score: Optional[float]
    touch_count: int
    formation_type: str
    detected_at: str
    last_touched_at: Optional[str] = None

    def __post_init__(self) -> None:
        if self.touch_count < 3:
            raise ValueError("Supply/demand level requires >= 3 touches")
        if self.strength_score is None:
            self.strength_score = self._compute_strength()

    def _compute_strength(self) -> float:
        range_width = max(self.price_high - self.price_low, 1.0)
        touch_factor = min(self.touch_count / 3.0, 2.0)
        recency_bonus = 1.0
        if self.last_touched_at:
            detected = _normalize_timestamp(self.detected_at)
            last = _normalize_timestamp(self.last_touched_at)
            days = max((detected - last).days, 0)
            recency_bonus = max(1.5 - days / 30, 0.5)
        strength = 40 * touch_factor + 40 * recency_bonus + 20 * min(2.0 / range_width, 1.0)
        return round(min(strength, 100.0), 2)

    def distance_to_price(self, price: float) -> float:
        midpoint = (self.price_high + self.price_low) / 2
        if midpoint == 0:
            return 0.0
        return round(abs(price - midpoint) / midpoint * 100, 2)
