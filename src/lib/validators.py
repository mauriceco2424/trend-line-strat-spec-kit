from __future__ import annotations

from datetime import datetime, timedelta


def ensure_touch_spacing(previous_index: int, current_index: int, min_spacing: int) -> None:
    if current_index - previous_index < min_spacing:
        raise ValueError(
            f"Touch points too close together: prev={previous_index}, current={current_index}, min={min_spacing}"
        )


def ensure_distance_tolerance(distance_pct: float, max_distance_pct: float) -> None:
    if abs(distance_pct) > max_distance_pct:
        raise ValueError(
            f"Touch point distance {distance_pct}% exceeds tolerance {max_distance_pct}%"
        )


def ensure_timestamp_order(previous: str, current: str) -> None:
    prev_dt = _normalize_timestamp(previous)
    current_dt = _normalize_timestamp(current)
    if current_dt <= prev_dt:
        raise ValueError("Timestamps must be strictly increasing")


def _normalize_timestamp(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        normalized = ts.replace("Z", "")
        if "T" not in normalized:
            return datetime.fromisoformat(normalized)
        date_part, time_part = normalized.split("T")
        offset_sign = 1
        offset_hours = 0
        offset_minutes = 0
        for sep in ("+", "-"):
            if sep in time_part[1:]:
                time_part, offset = time_part.split(sep, 1)
                offset_sign = 1 if sep == "+" else -1
                offset_hours, offset_minutes = [int(part) for part in offset.split(":")]
                break
        hour, minute, second = [int(part) for part in time_part.split(":")]
        base = datetime.fromisoformat(f"{date_part}T00:00:00")
        extra_days, hour = divmod(hour, 24)
        result = base + timedelta(days=extra_days, hours=hour, minutes=minute, seconds=second)
        if offset_hours or offset_minutes:
            result -= offset_sign * timedelta(hours=offset_hours, minutes=offset_minutes)
        return result
