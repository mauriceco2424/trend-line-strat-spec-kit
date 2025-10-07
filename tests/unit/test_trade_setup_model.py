import pytest

from src.models.trade_setup import TradeSetup


def test_trade_setup_requires_a_plus_conditions():
    setup = TradeSetup(
        id="00000000-0000-0000-0000-000000030001",
        trendline_id="00000000-0000-0000-0000-000000000001",
        breakout_id="00000000-0000-0000-0000-000000010001",
        timeframe="4h",
        confidence_score=88.0,
        quality_score=85.0,
        confluence_strength=90.0,
        confirmation_factors=["3+ touches", "SD aligned", "HTF aligned"],
        supply_demand_alignment=True,
        detected_at="2024-10-07T12:00:00Z",
    )

    assert setup.a_plus is True


def test_trade_setup_confluence_scoring_requires_alignment():
    with pytest.raises(ValueError):
        TradeSetup(
            id="00000000-0000-0000-0000-000000030002",
            trendline_id="00000000-0000-0000-0000-000000000001",
            breakout_id="00000000-0000-0000-0000-000000010001",
            timeframe="1h",
            confidence_score=40.0,
            quality_score=42.0,
            confluence_strength=30.0,
            confirmation_factors=["2 touches"],
            supply_demand_alignment=False,
            detected_at="2024-10-07T12:00:00Z",
        )
