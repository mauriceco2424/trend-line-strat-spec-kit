import pytest

from src.models.crypto_pair import CryptocurrencyPair


def test_crypto_pair_requires_top_50_rank():
    with pytest.raises(ValueError):
        CryptocurrencyPair(
            symbol="DOGEUSDT",
            base_asset="DOGE",
            quote_asset="USDT",
            market_cap_rank=75,
            current_price=0.067,
            last_price_update="2024-10-07T12:00:00Z",
            is_monitored=True,
            added_at="2024-07-01T00:00:00Z",
        )


def test_crypto_pair_hysteresis_allows_rank_58_when_monitored():
    pair = CryptocurrencyPair(
        symbol="SOLUSDT",
        base_asset="SOL",
        quote_asset="USDT",
        market_cap_rank=45,
        current_price=150.0,
        last_price_update="2024-10-07T12:00:00Z",
        is_monitored=True,
        added_at="2024-01-01T00:00:00Z",
    )

    pair.update_rank(58)
    assert pair.market_cap_rank == 58
    pair.update_rank(65)
    assert pair.is_monitored is False
