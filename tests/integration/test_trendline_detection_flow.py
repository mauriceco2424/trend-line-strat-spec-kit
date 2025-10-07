from src.services.trendline_detector import TrendlineDetector


def test_trendline_detection_flow(detection_candles) -> None:
    detector = TrendlineDetector()
    trendlines = detector.detect(pair_symbol="ETHUSDT", timeframe="4h", candles=detection_candles)

    assert trendlines, "Expected at least one trendline candidate"
    primary = trendlines[0]

    assert primary.pair_symbol == "ETHUSDT"
    assert primary.timeframe == "4h"
    assert primary.touch_point_count >= 3
    assert 0.0 <= primary.r_squared <= 1.0
    assert primary.quality_score > 0
    assert primary.direction in {"support", "resistance"}
