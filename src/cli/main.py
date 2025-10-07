from __future__ import annotations

from pathlib import Path

import typer

from src.cli.backtest_cmd import backtest_command
from src.cli.detect_cmd import detect_command

app = typer.Typer(help="Trendline breakout detection and backtesting CLI")


@app.command()
def detect(config: Path = typer.Option(..., exists=True, readable=True)) -> None:
    """Run detection against live data."""
    detect_command(config)


@app.command()
def backtest(config: Path = typer.Option(..., exists=True, readable=True)) -> None:
    """Run a backtest using the provided configuration file."""
    backtest_command(config)


if __name__ == "__main__":
    app()
