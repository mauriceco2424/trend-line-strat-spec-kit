from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

import pytest

CANDLE_INTERVAL_HOURS = 4


def _make_candle(timestamp: datetime, open_price: float, high: float, low: float, close: float, volume: float) -> Dict[str, float | str]:
    return {
        "timestamp": timestamp.isoformat(),
        "open": round(open_price, 2),
        "high": round(high, 2),
        "low": round(low, 2),
        "close": round(close, 2),
        "volume": round(volume, 2),
    }


def _generate_base_series() -> Tuple[List[Dict[str, float | str]], datetime, float]:
    base_time = datetime(2024, 9, 1, tzinfo=timezone.utc)
    slope = 12.0
    base_price = 1850.0
    candles: List[Dict[str, float | str]] = []
    last_close = base_price

    for idx in range(80):
        trend_price = base_price + slope * idx
        is_touch = idx in {12, 34, 56}
        low = trend_price - (22 if is_touch else 8)
        high = trend_price + 10
        close = trend_price + (6 if is_touch else 8)
        open_price = close - 4
        volume = 1800 + idx * 14
        timestamp = base_time + timedelta(hours=CANDLE_INTERVAL_HOURS * idx)
        candles.append(_make_candle(timestamp, open_price, high, low, close, volume))
        last_close = close

    last_timestamp = base_time + timedelta(hours=CANDLE_INTERVAL_HOURS * 79)
    return candles, last_timestamp, last_close


def _generate_breakout_sequence(start_time: datetime, last_close: float) -> List[Dict[str, float | str]]:
    breakout_volume = 6000.0
    retest_volume = 2500.0
    rejection_volume = 5200.0

    stage1_time = start_time + timedelta(hours=CANDLE_INTERVAL_HOURS)
    stage2_time = stage1_time + timedelta(hours=CANDLE_INTERVAL_HOURS)
    stage3_time = stage2_time + timedelta(hours=CANDLE_INTERVAL_HOURS)
    follow1_time = stage3_time + timedelta(hours=CANDLE_INTERVAL_HOURS)
    follow2_time = follow1_time + timedelta(hours=CANDLE_INTERVAL_HOURS)

    breakout_close = last_close + 80
    retest_close = breakout_close - 40
    rejection_close = breakout_close + 60

    stage1 = _make_candle(
        stage1_time,
        last_close + 5,
        breakout_close + 35,
        last_close - 5,
        breakout_close,
        breakout_volume,
    )
    stage2 = _make_candle(
        stage2_time,
        breakout_close - 20,
        breakout_close + 10,
        last_close - 10,
        retest_close,
        retest_volume,
    )
    stage3 = _make_candle(
        stage3_time,
        retest_close,
        rejection_close + 20,
        retest_close - 5,
        rejection_close,
        rejection_volume,
    )
    follow1 = _make_candle(
        follow1_time,
        rejection_close,
        rejection_close + 45,
        rejection_close - 20,
        rejection_close + 30,
        3100.0,
    )
    follow2 = _make_candle(
        follow2_time,
        rejection_close + 10,
        rejection_close + 80,
        rejection_close - 5,
        rejection_close + 70,
        2900.0,
    )

    return [stage1, stage2, stage3, follow1, follow2]


@pytest.fixture(scope="module")
def detection_candles() -> List[Dict[str, float | str]]:
    candles, _, _ = _generate_base_series()
    return candles


@pytest.fixture(scope="module")
def breakout_extension() -> List[Dict[str, float | str]]:
    base_candles, last_timestamp, last_close = _generate_base_series()
    return _generate_breakout_sequence(last_timestamp, last_close)


@pytest.fixture(scope="module")
def full_breakout_series(detection_candles: List[Dict[str, float | str]], breakout_extension: List[Dict[str, float | str]]) -> List[Dict[str, float | str]]:
    return [*detection_candles, *breakout_extension]


@pytest.fixture(scope="module")
def backtest_candles(full_breakout_series: List[Dict[str, float | str]]) -> List[Dict[str, float | str]]:
    extended_follow_through: List[Dict[str, float | str]] = []
    if full_breakout_series:
        last_timestamp = datetime.fromisoformat(full_breakout_series[-1]["timestamp"])
        last_close = float(full_breakout_series[-1]["close"])
    else:
        base_time = datetime(2024, 9, 1, tzinfo=timezone.utc)
        last_timestamp = base_time
        last_close = 1850.0

    for idx in range(1, 11):
        ts = last_timestamp + timedelta(hours=CANDLE_INTERVAL_HOURS * idx)
        close = last_close + 20 * idx
        extended_follow_through.append(
            _make_candle(ts, close - 5, close + 15, close - 25, close, 2600.0 + idx * 50)
        )

    return [*full_breakout_series, *extended_follow_through]
