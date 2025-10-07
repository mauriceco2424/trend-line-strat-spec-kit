# Trendline Breakout Detection System

A Python 3.11 project for detecting, ranking, and backtesting cryptocurrency trendline breakouts using a test-first workflow.

## Features
- Contract, integration, and unit tests covering detection, ranking, and backtesting flows
- Shared libraries for timeframe utilities, validators, and SQLite persistence
- Services for price fetching, trendline analysis, supply/demand detection, breakout confirmation, and trade ranking
- Typer-based CLI with `detect` and `backtest` commands

## Getting Started
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1  # Windows PowerShell
pip install -e .[dev]
```
> If `python-binance` cannot be installed or credentials are absent, the price fetcher falls back to synthetic OHLCV data.

## Running Tests
```bash
pytest
```
The current suite reports **47 passed** with ~90% coverage. Coverage gaps are primarily in CLI presentation paths and validator guard clauses; see the coverage summary printed by pytest for exact lines.

## CLI Usage
Sample configuration files live in `configs/`:
- `detect_example.json`
- `backtest_example.json`

Run detection:
```bash
python -m src.cli.main detect --config configs/detect_example.json
```
Run backtest:
```bash
python -m src.cli.main backtest --config configs/backtest_example.json
```
Outputs are streamed as JSON via `rich`. Edit the config files to experiment with other pairs, timeframes, or balances.

## Performance Snapshot
Using the bundled configs on synthetic data:
- Detection pipeline: ~1.24s
- Backtest pipeline: ~1.40s

These timings fall well within the 5-minute refresh goal. Expect higher latency when live Binance data is enabled.

## Documentation
- `specs/001-trendline-breakout/quickstart.md` – end-to-end setup & CLI walkthrough
- `specs/001-trendline-breakout/spec.md` – functional requirements and scenarios
- `specs/001-trendline-breakout/tasks.md` – task checklist (T001–T048)
- `specs/001-trendline-breakout/changelog.md` – recent documentation & validation notes

## Project Layout
```
src/
  cli/                # Typer commands and console wiring
  contracts/          # JSON schema loader utilities
  lib/                # Shared timeframe, validator, storage helpers
  models/             # Dataclasses for trendlines, breakouts, setups, etc.
  services/           # Detection, ranking, and backtest services
tests/
  contract/           # Contract tests targeting JSON schemas
  integration/        # End-to-end flow tests
  unit/               # Unit & service-level tests
configs/              # Example CLI configuration files
data/                 # Cache directory and SQLite schema/docs
```

## Next Steps
- Extend CLI coverage with golden-output tests
- Integrate live Binance credentials and cache directories for production workloads
- Monitor performance when scaling universe size or timeframes

