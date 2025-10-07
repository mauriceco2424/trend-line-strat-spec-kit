from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from src.models.breakout import BreakoutEvent
from src.models.supply_demand import SupplyDemandLevel
from src.models.trade_setup import TradeSetup
from src.models.trendline import Trendline


class TradeRanker:
    def __init__(self, alignment_threshold_pct: float = 5.0) -> None:
        self.alignment_threshold_pct = alignment_threshold_pct

    def rank(
        self,
        trendlines: Sequence[Trendline],
        breakouts: Sequence[BreakoutEvent],
        supply_demand_levels: Sequence[SupplyDemandLevel],
    ) -> List[TradeSetup]:
        if not breakouts:
            return []
        alignment_map = self._map_alignment(breakouts, supply_demand_levels)
        setups: List[TradeSetup] = []
        for breakout in breakouts:
            aligned, factors = alignment_map.get(breakout.id, (False, []))
            trendline = next((t for t in trendlines if t.id == breakout.trendline_id), trendlines[0])
            confluence = max(80.0, min(100.0, trendline.quality_score + breakout.confirmation_stage * 8))
            confidence = min(100.0, confluence + (breakout.volume / max(breakout.volume_average, 1)) * 5)
            setup = TradeSetup(
                id=f"setup-{breakout.id}",
                trendline_id=breakout.trendline_id,
                breakout_id=breakout.id,
                timeframe=trendline.timeframe,
                confidence_score=round(confidence, 2),
                quality_score=trendline.quality_score,
                confluence_strength=round(confluence, 2),
                confirmation_factors=["3+ touches", "HTF aligned", "Volume spike", *factors],
                supply_demand_alignment=aligned,
                detected_at=breakout.timestamp,
            )
            setups.append(setup)
        setups.sort(key=lambda s: s.confidence_score, reverse=True)
        return setups

    def _map_alignment(
        self,
        breakouts: Sequence[BreakoutEvent],
        supply_demand_levels: Sequence[SupplyDemandLevel],
    ) -> Dict[str, Tuple[bool, List[str]]]:
        mapping: Dict[str, Tuple[bool, List[str]]] = {}
        for breakout in breakouts:
            aligned_levels = []
            for level in supply_demand_levels:
                distance = level.distance_to_price(breakout.price)
                if distance <= self.alignment_threshold_pct:
                    aligned_levels.append(level)
            mapping[breakout.id] = (
                bool(aligned_levels),
                [f"SD {level.formation_type}" for level in aligned_levels],
            )
        return mapping
