import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from src.cli.main import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def config_files(tmp_path: Path):
    backtest = tmp_path / "backtest_config.json"
    backtest.write_text(
        json.dumps(
            {
                "pair_symbol": "ETHUSDT",
                "timeframe": "4h",
                "initial_balance": 10000.0,
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
            }
        )
    )

    detect = tmp_path / "detect_config.json"
    detect.write_text(
        json.dumps(
            {
                "pair_symbol": "ETHUSDT",
                "timeframe": "4h",
                "universe_size": 50,
            }
        )
    )
    return backtest, detect


def test_cli_backtest_runs_with_config(runner, config_files):
    backtest_cfg, _ = config_files
    with patch("src.cli.backtest_cmd.run_backtest") as mock_run:
        mock_run.return_value = {
            "trades": [],
            "metrics": {
                "sortino_ratio": 1.5,
                "profit_factor": 2.1,
                "max_drawdown": -0.12,
            },
            "summary": {"total_breakouts": 0},
        }
        result = runner.invoke(app, ["backtest", "--config", str(backtest_cfg)])
    assert result.exit_code == 0


def test_cli_detect_streams_results(runner, config_files):
    _, detect_cfg = config_files
    with patch("src.cli.detect_cmd.run_detection") as mock_run:
        mock_run.return_value = []
        result = runner.invoke(app, ["detect", "--config", str(detect_cfg)])
    assert result.exit_code == 0
