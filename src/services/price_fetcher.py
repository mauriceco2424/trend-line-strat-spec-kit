from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


class PriceFetcher:
    def __init__(self, cache_dir: Optional[Path | str] = None, universe_size: int = 50) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.universe_size = universe_size
        self.universe: List[str] = []
        self._client: Any = None

    async def ensure_client(self) -> None:
        if self._client is not None:
            return
        try:
            from binance import AsyncClient  # type: ignore

            self._client = await AsyncClient.create()
        except Exception:
            self._client = None

    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> List[Dict[str, Any]]:
        await self.ensure_client()
        candles: List[Dict[str, Any]]
        if self._client is None:
            candles = self._generate_synthetic_series(limit)
        else:
            interval = self._interval_for_timeframe(timeframe)
            raw = await self._client.get_klines(symbol=symbol, interval=interval, limit=limit)
            candles = [
                {
                    "timestamp": datetime.fromtimestamp(item[0] / 1000, tz=timezone.utc).isoformat(),
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5]),
                }
                for item in raw
            ]

        if self.cache_dir:
            cache_path = self.cache_dir / f"{symbol}_{timeframe}.json"
            cache_path.write_text(json.dumps(candles), encoding="utf-8")
        return candles

    async def refresh_universe(self) -> None:
        ranks = await self._fetch_market_cap_ranks()
        self.universe = [symbol for symbol, _ in ranks[: self.universe_size]]

    async def _fetch_market_cap_ranks(self) -> Sequence[Tuple[str, int]]:
        return [("BTCUSDT", 1), ("ETHUSDT", 2), ("BNBUSDT", 3)]

    async def close(self) -> None:
        if self._client is not None:
            try:
                await self._client.close_connection()
            finally:
                self._client = None

    @staticmethod
    def _interval_for_timeframe(timeframe: str) -> str:
        mapping = {
            "1h": "1h",
            "4h": "4h",
            "daily": "1d",
            "weekly": "1w",
        }
        return mapping.get(timeframe, "1h")

    @staticmethod
    def _generate_synthetic_series(limit: int) -> List[Dict[str, Any]]:
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)
        return [
            {
                "timestamp": (base + timedelta(hours=4 * idx)).isoformat(),
                "open": 2000 + idx * 5,
                "high": 2000 + idx * 5 + 10,
                "low": 2000 + idx * 5 - 10,
                "close": 2000 + idx * 5 + 5,
                "volume": 1000 + idx * 20,
            }
            for idx in range(limit)
        ]


