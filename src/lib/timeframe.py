from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Union


class Timeframe(Enum):
    """Supported analysis timeframes."""

    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAILY = "daily"
    WEEKLY = "weekly"

    @classmethod
    def from_str(cls, value: str | "Timeframe") -> "Timeframe":
        if isinstance(value, Timeframe):
            return value
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Unsupported timeframe: {value}")


_WEIGHT_MAP = {
    Timeframe.HOUR_1: 1.0,
    Timeframe.HOUR_4: 2.0,
    Timeframe.DAILY: 3.0,
    Timeframe.WEEKLY: 4.0,
}


def weight_for_timeframe(timeframe: Union[str, Timeframe]) -> float:
    tf = Timeframe.from_str(timeframe)
    return _WEIGHT_MAP[tf]


def adaptive_horizon(timeframe: Union[str, Timeframe]) -> int:
    tf = Timeframe.from_str(timeframe)
    horizon_map = {
        Timeframe.HOUR_1: 90,
        Timeframe.HOUR_4: 180,
        Timeframe.DAILY: 365,
        Timeframe.WEEKLY: 365 * 2,
    }
    return horizon_map[tf]


def next_update_schedule(timeframe: Union[str, Timeframe]) -> timedelta:
    tf = Timeframe.from_str(timeframe)
    mapping = {
        Timeframe.HOUR_1: timedelta(hours=1),
        Timeframe.HOUR_4: timedelta(hours=4),
        Timeframe.DAILY: timedelta(days=1),
        Timeframe.WEEKLY: timedelta(days=7),
    }
    return mapping[tf]
