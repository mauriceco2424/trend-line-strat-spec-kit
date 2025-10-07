from src.services.breakout_detector import BreakoutDetector
from src.services.trendline_detector import TrendlineDetector


def test_breakout_detection_flow(detection_candles, breakout_extension) -> None:
    detector = TrendlineDetector()
    trendlines = detector.detect("ETHUSDT", "4h", detection_candles)
    assert trendlines, "Trendline detection failed to produce candidates"

    breakout_detector = BreakoutDetector(retest_window=5)
    combined_series = [*detection_candles, *breakout_extension]
    events = breakout_detector.detect(trendlines[0], combined_series)

    assert events, "Expected at least one breakout event"
    primary = events[0]

    assert primary.direction == "upward"
    assert primary.confirmation_stage == 3
    assert primary.trendline_id == trendlines[0].id
    assert primary.retest is not None
    assert primary.rejection is not None
