from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class TradeSetup:
    id: str
    trendline_id: str
    breakout_id: str
    timeframe: str
    confidence_score: float
    quality_score: float
    confluence_strength: float
    confirmation_factors: List[str]
    supply_demand_alignment: bool
    detected_at: str
    a_plus: bool = field(init=False)

    def __post_init__(self) -> None:
        if not self.confirmation_factors:
            raise ValueError("Trade setup requires confirmation factors")
        if not self.supply_demand_alignment and self.confluence_strength < 60:
            raise ValueError("Non-aligned setups must meet minimum confluence strength")
        self.a_plus = self._is_a_plus()

    def _is_a_plus(self) -> bool:
        return self.supply_demand_alignment and self.confluence_strength >= 80
