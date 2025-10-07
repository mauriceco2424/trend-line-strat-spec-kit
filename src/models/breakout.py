from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.lib.validators import ensure_timestamp_order


@dataclass
class BreakoutStage:
    timestamp: str
    price: float
    magnitude_pct: Optional[float] = None


@dataclass
class BreakoutEvent:
    id: str
    trendline_id: str
    direction: str
    timestamp: str
    price: float
    confirmation_stage: int
    initial_break: BreakoutStage
    retest: Optional[BreakoutStage]
    rejection: Optional[BreakoutStage]
    volume: float
    volume_average: float

    def advance_stage(self, stage: int, stage_payload: dict) -> None:
        if stage != self.confirmation_stage + 1:
            raise ValueError("Stage progression must be sequential")

        ts = stage_payload["timestamp"]
        ensure_timestamp_order(self._latest_stage_timestamp(), ts)
        new_stage = BreakoutStage(
            timestamp=ts,
            price=float(stage_payload["price"]),
            magnitude_pct=stage_payload.get("magnitude_pct"),
        )

        if stage == 2:
            self.retest = new_stage
        elif stage == 3:
            if self.retest is None:
                raise ValueError("Cannot reach rejection without retest")
            self.rejection = new_stage
        else:
            raise ValueError("Unsupported stage")

        self.confirmation_stage = stage

    def _latest_stage_timestamp(self) -> str:
        if self.rejection is not None:
            return self.rejection.timestamp
        if self.retest is not None:
            return self.retest.timestamp
        return self.initial_break.timestamp

    @property
    def is_confirmed(self) -> bool:
        return self.confirmation_stage == 3
