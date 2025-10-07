from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CryptocurrencyPair:
    symbol: str
    base_asset: str
    quote_asset: str
    market_cap_rank: int
    current_price: float
    last_price_update: str
    is_monitored: bool
    added_at: str
    removed_at: str | None = None

    def __post_init__(self) -> None:
        if self.is_monitored and self.market_cap_rank > 50:
            raise ValueError("Monitored pairs must be within top 50")

    def update_rank(self, new_rank: int) -> None:
        self.market_cap_rank = new_rank
        if new_rank > 60:
            self.is_monitored = False
