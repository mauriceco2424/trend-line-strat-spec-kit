import pytest

from src.lib.timeframe import Timeframe
from src.lib.timeframe import weight_for_timeframe
from src.lib.timeframe import adaptive_horizon
from src.lib.timeframe import next_update_schedule


def test_timeframe_enum_contains_expected_members():
    assert list(Timeframe) == [
        Timeframe.HOUR_1,
        Timeframe.HOUR_4,
        Timeframe.DAILY,
        Timeframe.WEEKLY,
    ]


def test_weight_for_timeframe():
    assert weight_for_timeframe(Timeframe.WEEKLY) > weight_for_timeframe(Timeframe.HOUR_1)


def test_adaptive_horizon_returns_longer_for_higher_timeframe():
    h1_span = adaptive_horizon(Timeframe.HOUR_1)
    daily_span = adaptive_horizon(Timeframe.DAILY)
    assert daily_span > h1_span


def test_next_update_schedule_weekly_returns_seven_days():
    delta = next_update_schedule(Timeframe.WEEKLY)
    assert delta.days == 7


def test_invalid_timeframe_raises():
    with pytest.raises(ValueError):
        weight_for_timeframe("monthly")
