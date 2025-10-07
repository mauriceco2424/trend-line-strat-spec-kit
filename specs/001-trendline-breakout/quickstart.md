# Quickstart: Trendline Breakout Detection System

This guide walks you through installing dependencies, running the contract/test suite, and exercising the CLI flows that power the trendline breakout detection project.

## Prerequisites
- Python 3.11+
- Recommended: virtual environment (`python -m venv .venv` and activate)
- Optional: Binance API credentials (the system falls back to synthetic data when the python-binance client is unavailable)

## 1. Install dependencies
```bash
pip install -e .[dev]
```
This installs runtime libraries (`pandas`, `numpy`, `scipy`, `requests`, `python-binance`, `optuna`, `typer`, etc.) along with developer tooling (`pytest`, `pytest-cov`, `jsonschema`, `ruff`, `black`, `mypy`).

## 2. Run the automated test suite
```bash
pytest
```
A healthy run should report 47 passing tests with overall coverage around 90%. Coverage gaps currently include CLI output branches and some validator guard clauses—see the coverage summary for exact line references.

## 3. Prepare CLI configuration
Example config files live under `configs/`:
- `configs/detect_example.json` – minimal settings for a detection pass
- `configs/backtest_example.json` – detection inputs plus an `initial_balance` used by the backtester

Each file must define at least:
```json
{
  "pair_symbol": "ETHUSDT",
  "timeframe": "4h",
  "universe_size": 25,
  "initial_balance": 10000
}
```
`initial_balance` is optional for detection runs.

## 4. Run the detection CLI
```bash
python -m src.cli.main detect --config configs/detect_example.json
```
Expected output (synthetic data path):
```json
[
  {
    "trendline_id": "trendline-0001",
    "breakout_id": "breakout-0001",
    "confidence_score": 100.0,
    "a_plus": false
  }
]
```
If Binance credentials are available, live OHLCV data is fetched before producing ranked setups.

## 5. Run the backtest CLI
```bash
python -m src.cli.main backtest --config configs/backtest_example.json
```
Sample output:
```json
{
  "trades": [
    {"entry": 4708.81, "exit": 4944.250500000001}
  ],
  "metrics": {
    "sortino_ratio": 235.4405,
    "profit_factor": 235.4405,
    "max_drawdown": -0.05
  },
  "summary": {
    "total_breakouts": 1.0,
    "total_trades": 1.0
  }
}
```

## 6. Next steps
- Tweak universe size, timeframe, or initial balance in the configs to explore other scenarios.
- Use `pytest --cov` to monitor coverage improvements as you implement additional flows.
- After verifying outputs, update documentation and changelogs (see T048) and consider performance profiling (T047) if you are targeting the 5-minute refresh cadence.

## Troubleshooting
| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| `ModuleNotFoundError: binance` | `python-binance` extras missing | Ensure `pip install -e .[dev]` completed; CLI falls back to synthetic data if install fails |
| CLI prints "No trade setups detected" | Price series lacks qualifying breakouts | Increase candle limit or try another pair/timeframe |
| pytest fails due to coverage gating | Coverage is below targets | Exercise CLI commands to cover missing paths or add targeted tests |

