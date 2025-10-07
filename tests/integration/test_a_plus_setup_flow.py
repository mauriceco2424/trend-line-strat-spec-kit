from src.services.breakout_detector import BreakoutDetector
from src.services.supply_demand_detector import SupplyDemandDetector
from src.services.trade_ranker import TradeRanker
from src.services.trendline_detector import TrendlineDetector


def test_a_plus_setup_flow(detection_candles, breakout_extension) -> None:
    trendline_detector = TrendlineDetector()
    trendlines = trendline_detector.detect("ETHUSDT", "4h", detection_candles)
    assert trendlines, "No trendlines detected"
    trendline = trendlines[0]

    breakout_detector = BreakoutDetector()
    combined = [*detection_candles, *breakout_extension]
    breakouts = breakout_detector.detect(trendline, combined)
    assert breakouts, "No breakout events detected"

    sd_detector = SupplyDemandDetector(distance_threshold_pct=2.0)
    sd_levels = sd_detector.detect("ETHUSDT", "4h", combined)
    assert sd_levels, "Expected supply/demand levels"

    ranker = TradeRanker()
    setups = ranker.rank(trendlines, breakouts, sd_levels)

    assert setups, "Expected at least one ranked setup"
    top = setups[0]
    assert top.a_plus is True
    assert "Volume spike" in top.confirmation_factors
    assert top.trendline_id == trendline.id
    assert top.breakout_id == breakouts[0].id
