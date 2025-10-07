import pytest

from src.models.trendline import Trendline
from src.models.trendline import TouchPoint


@pytest.fixture
def sample_touch_points():
    return [
        TouchPoint(
            id="00000000-0000-0000-0000-000000000101",
            timestamp="2024-09-05T00:00:00Z",
            price=1900.0,
            distance_from_line=0.5,
            is_confirmed=True,
            candle_type="wick",
            candles_since_previous=None,
        ),
        TouchPoint(
            id="00000000-0000-0000-0000-000000000102",
            timestamp="2024-09-10T00:00:00Z",
            price=1920.0,
            distance_from_line=-0.3,
            is_confirmed=True,
            candle_type="body",
            candles_since_previous=20,
        ),
        TouchPoint(
            id="00000000-0000-0000-0000-000000000103",
            timestamp="2024-09-20T00:00:00Z",
            price=1950.0,
            distance_from_line=0.2,
            is_confirmed=False,
            candle_type="wick",
            candles_since_previous=30,
        ),
    ]


def test_trendline_requires_three_touch_points(sample_touch_points):
    with pytest.raises(ValueError):
        Trendline(
            id="00000000-0000-0000-0000-000000000001",
            pair_symbol="ETHUSDT",
            direction="support",
            timeframe="4h",
            slope=1.2,
            intercept=1850.0,
            r_squared=0.8,
            quality_score=75.0,
            created_at="2024-09-01T00:00:00Z",
            last_updated="2024-09-05T00:00:00Z",
            is_valid=True,
            touch_points=sample_touch_points[:2],
        )


def test_trendline_quality_score_weighted(sample_touch_points):
    trendline = Trendline(
        id="00000000-0000-0000-0000-000000000001",
        pair_symbol="ETHUSDT",
        direction="support",
        timeframe="daily",
        slope=0.8,
        intercept=1800.0,
        r_squared=0.9,
        quality_score=None,
        created_at="2024-09-01T00:00:00Z",
        last_updated="2024-10-01T00:00:00Z",
        is_valid=True,
        touch_points=sample_touch_points,
    )

    assert trendline.quality_score > 0
    assert trendline.touch_point_count == 3
    assert trendline.touch_distribution_score is not None


def test_trendline_state_transitions(sample_touch_points):
    trendline = Trendline(
        id="00000000-0000-0000-0000-000000000001",
        pair_symbol="ETHUSDT",
        direction="resistance",
        timeframe="4h",
        slope=1.5,
        intercept=2000.0,
        r_squared=0.88,
        quality_score=80.0,
        created_at="2024-09-01T00:00:00Z",
        last_updated="2024-09-10T00:00:00Z",
        is_valid=True,
        touch_points=sample_touch_points,
    )

    trendline.mark_broken()
    assert trendline.is_valid is False
    trendline.revalidate()
    assert trendline.is_valid is True
