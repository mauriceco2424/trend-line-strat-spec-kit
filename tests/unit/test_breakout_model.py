import pytest

from src.models.breakout import BreakoutEvent
from src.models.breakout import BreakoutStage


@pytest.fixture
def base_stage():
    return BreakoutStage(
        timestamp="2024-10-07T08:00:00Z",
        price=2010.0,
        magnitude_pct=None,
    )


@pytest.fixture
def breakout_event(base_stage):
    return BreakoutEvent(
        id="00000000-0000-0000-0000-000000010001",
        trendline_id="00000000-0000-0000-0000-000000000001",
        direction="upward",
        timestamp="2024-10-07T12:00:00Z",
        price=2050.0,
        confirmation_stage=1,
        initial_break=base_stage,
        retest=None,
        rejection=None,
        volume=5000.0,
        volume_average=2300.0,
    )


def test_breakout_stage_progression_requires_order(breakout_event):
    with pytest.raises(ValueError):
        breakout_event.advance_stage(stage=3, stage_payload={"timestamp": "2024-10-07T10:00:00Z", "price": 2040.0, "magnitude_pct": 1.2})


def test_breakout_event_tracks_retest_and_rejection(breakout_event):
    breakout_event.advance_stage(stage=2, stage_payload={"timestamp": "2024-10-07T10:00:00Z", "price": 2030.0})
    assert breakout_event.retest is not None

    breakout_event.advance_stage(stage=3, stage_payload={"timestamp": "2024-10-07T11:00:00Z", "price": 2075.0, "magnitude_pct": 1.5})
    assert breakout_event.rejection is not None
    assert breakout_event.confirmation_stage == 3
