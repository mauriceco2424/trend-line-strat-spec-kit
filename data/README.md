# Data Directory

This folder stores runtime data used by the trendline breakout backtesting system.

- `cache/`: Cached OHLCV responses and derived features. Files are organized by symbol and timeframe and refreshed automatically. Old cache files may be deleted when stale.
- `db/`: SQLite databases created from `schema.sql`. The active database lives in this directory, while archival tables keep long-term history per the retention policy.

Retention policy aligns with the spec:

- Active trendline, breakout, and setup records for the past 12 months remain in the primary tables.
- Historical records older than 12 months are migrated to archive tables but preserved indefinitely.
- Cache files should be pruned periodically to balance disk usage with reproducibility.
