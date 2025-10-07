import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.price_fetcher import PriceFetcher


@pytest.mark.asyncio
async def test_price_fetcher_fetches_and_caches(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    fetcher = PriceFetcher(cache_dir=cache_dir, universe_size=50)

    mock_client = AsyncMock()
    mock_client.get_klines.return_value = [[1, 2, 3, 4, 5, 1000]] * 10
    fetcher._client = mock_client

    candles = await fetcher.fetch_ohlcv("BTCUSDT", "4h", limit=10)
    assert len(candles) == 10
    assert any(cache_dir.iterdir())


@pytest.mark.asyncio
async def test_price_fetcher_refreshes_top_universe():
    fetcher = PriceFetcher(cache_dir=None, universe_size=50)
    fetcher._fetch_market_cap_ranks = AsyncMock(return_value=[("BTCUSDT", 1), ("ETHUSDT", 2)])
    await fetcher.refresh_universe()
    assert "BTCUSDT" in fetcher.universe
