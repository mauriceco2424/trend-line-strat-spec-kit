import pytest

from src.lib.validators import ensure_touch_spacing
from src.lib.validators import ensure_distance_tolerance
from src.lib.validators import ensure_timestamp_order


def test_ensure_touch_spacing_rejects_close_candles():
    with pytest.raises(ValueError):
        ensure_touch_spacing(previous_index=10, current_index=12, min_spacing=5)


def test_ensure_distance_tolerance_passes_within_bounds():
    ensure_distance_tolerance(distance_pct=0.8, max_distance_pct=1.0)


def test_ensure_distance_tolerance_fails_outside_bounds():
    with pytest.raises(ValueError):
        ensure_distance_tolerance(distance_pct=2.5, max_distance_pct=1.0)


def test_timestamp_order_raises_for_out_of_order():
    with pytest.raises(ValueError):
        ensure_timestamp_order(previous="2024-10-07T12:00:00Z", current="2024-10-06T12:00:00Z")
