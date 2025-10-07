# Tasks: Trendline Breakout Detection System

**Input**: Design documents from `/specs/001-trendline-breakout/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/ (generated in T005)

## Phase 3.1: Setup
- [ ] T001 Create project skeleton (`src/models`, `src/services`, `src/cli`, `src/lib`, `tests/{contract,integration,unit,cli}`, `data/cache`, `data/db`) with `__init__.py` placeholders so the repository matches the structure in plan.md.
- [ ] T002 Initialize `pyproject.toml` with project metadata, Python 3.11 requirement, src-layout packaging, and runtime dependencies (pandas, numpy, scipy, requests, python-binance, optuna, sqlite3 bindings) plus testing tools (pytest, pytest-cov, jsonschema).
- [ ] T003 Configure developer tooling by adding formatting/lint/type-check settings (`tool.black`, `tool.ruff`, `tool.mypy`) and a `pytest.ini` that enables strict warnings and coverage targets >80% for core modules.
- [ ] T004 Prepare data directories by adding `.gitkeep` files, drafting `data/db/schema.sql` with tables for Trendline, TouchPoint, BreakoutEvent, SupplyDemandLevel, APlusTradeSetup, and CryptocurrencyPair, and documenting cache retention policy in `data/README.md`.
- [ ] T005 Author JSON schemas under `specs/001-trendline-breakout/contracts/` (price-data-api.json, trendline-detection.json, breakout-detection.json, trade-ranking.json) that mirror the entities and validation rules from data-model.md for reuse in contract tests.

## Phase 3.2: Tests First (TDD) – all tests must fail before implementation
- [ ] T006 [P] Write failing contract test `tests/contract/test_price_api_contract.py` covering GET price data schema (symbol, timeframe enums, OHLCV with volume) against `contracts/price-data-api.json`.
- [ ] T007 [P] Write failing contract test `tests/contract/test_trendline_contract.py` validating trendline detection payload structure (3+ touch points, slope, quality metrics) using `contracts/trendline-detection.json`.
- [ ] T008 [P] Write failing contract test `tests/contract/test_breakout_contract.py` verifying breakout confirmation stages, retest data, and direction fields using `contracts/breakout-detection.json`.
- [ ] T009 [P] Write failing contract test `tests/contract/test_trade_ranking_contract.py` ensuring ranked setup output (scores, confluence factors, A+ flag) matches `contracts/trade-ranking.json`.
- [ ] T010 [P] Create failing integration test `tests/integration/test_trendline_detection_flow.py` that feeds OHLCV fixtures and expects ranked trendlines across 1h/4h/daily timeframes for scenario 1.
- [ ] T011 [P] Create failing integration test `tests/integration/test_breakout_detection_flow.py` exercising three-stage breakout confirmation with volume filter and retest rejection.
- [ ] T012 [P] Create failing integration test `tests/integration/test_a_plus_setup_flow.py` covering multi-confirmation A+ trade setup (trendline break + supply/demand alignment + higher timeframe bias).
- [ ] T013 [P] Create failing integration test `tests/integration/test_backtest_flow.py` that runs a sample backtest and asserts Sortino ratio, profit factor, and max drawdown reporting.
- [ ] T014 [P] Add failing unit tests in `tests/unit/test_trendline_model.py` for Trendline validations (>=3 touch points, timeframe enum, quality scoring weights, R-squared range).
- [ ] T015 [P] Add failing unit tests in `tests/unit/test_breakout_model.py` for BreakoutEvent stage transitions, timestamp ordering, and direction alignment with parent trendline.
- [ ] T016 [P] Add failing unit tests in `tests/unit/test_supply_demand_model.py` checking zone strength scoring, 2% proximity rule, and order-block validation flags.
- [ ] T017 [P] Add failing unit tests in `tests/unit/test_trade_setup_model.py` verifying confluence scoring, confirmation factors list, and A+ qualification rules.
- [ ] T018 [P] Add failing unit tests in `tests/unit/test_crypto_pair_model.py` enforcing top-50 market-cap constraints, hysteresis buffer, and monitoring state transitions.
- [ ] T019 [P] Add failing unit tests in `tests/unit/test_validators.py` covering shared validators (distance tolerance, temporal ordering, timeframe hierarchy checks).
- [ ] T020 [P] Add failing unit tests in `tests/unit/test_timeframe_utils.py` for timeframe weighting, adaptive horizon selection, and update cadence utilities.
- [ ] T021 [P] Add failing unit tests in `tests/unit/test_data_storage.py` for SQLite schema migration, historical retention splits, and archival view queries.
- [ ] T022 [P] Add failing service tests in `tests/unit/test_price_fetcher_service.py` for Binance client pagination, top-50 list refresh, and caching behaviour.
- [ ] T023 [P] Add failing service tests in `tests/unit/test_trendline_detector_service.py` covering pivot detection, regression refinement, and quality scoring outputs.
- [ ] T024 [P] Add failing service tests in `tests/unit/test_supply_demand_detector_service.py` for consolidation zone detection, order-block confirmation, and strength ranking.
- [ ] T025 [P] Add failing service tests in `tests/unit/test_breakout_detector_service.py` verifying three-stage confirmation workflow, retest window limits, and volume filter thresholds.
- [ ] T026 [P] Add failing service tests in `tests/unit/test_trade_ranker_service.py` for confluence scoring, timeframe weighting, and A+ prioritisation logic.
- [ ] T027 [P] Add failing service tests in `tests/unit/test_backtester_service.py` covering rolling metric calculations, consistency with live detectors, and data retention.
- [ ] T028 [P] Add failing CLI tests in `tests/cli/test_cli_commands.py` exercising `detect` and `backtest` commands via `CliRunner`, ensuring config loading and output artefacts are produced.

## Phase 3.3: Core Implementation (make the failing tests pass in order)
- [ ] T029 Implement `src/lib/timeframe.py` utilities for timeframe enums, weighting, adaptive horizons, and weekly market-cap refresh scheduling.
- [ ] T030 Implement `src/lib/validators.py` with reusable validators (touch spacing, distance tolerance, timestamp ordering, confirmation preconditions) referenced by models and services.
- [ ] T031 Implement `src/lib/data_storage.py` providing SQLite connection management, schema migrations aligned with `data/db/schema.sql`, archived table views, and caching helpers.
- [ ] T032 [P] Implement `src/models/trendline.py` (dataclasses for Trendline + TouchPoint, quality scoring, derived metrics, state transitions) to satisfy trendline model tests.
- [ ] T033 [P] Implement `src/models/breakout.py` encapsulating breakout stages, retest tracking, direction validation, and persistence payloads.
- [ ] T034 [P] Implement `src/models/supply_demand.py` with zone identification attributes, strength scoring, and proximity checks.
- [ ] T035 [P] Implement `src/models/trade_setup.py` composing trendline, breakout, and supply/demand data into ranked setups with confluence scoring.
- [ ] T036 [P] Implement `src/models/crypto_pair.py` managing market-cap rank, monitoring states, and helper methods for active trendlines/setups.
- [ ] T037 Implement `src/services/price_fetcher.py` to source OHLCV + volume data from Binance, enforce rate-limit friendly batching, maintain top-50 universe with hysteresis, and write cache files.
- [ ] T038 Implement `src/services/trendline_detector.py` applying pivot-based detection, regression refinement, R-squared filtering, and quality ranking across timeframes.
- [ ] T039 Implement `src/services/supply_demand_detector.py` to identify consolidation/order-block zones, score strength, and determine alignment with breakout direction.
- [ ] T040 Implement `src/services/breakout_detector.py` executing the three-stage confirmation workflow, managing retest windows, and tagging volume confirmation.
- [ ] T041 Implement `src/services/trade_ranker.py` combining trendlines, breakouts, supply/demand levels, and timeframe bias into ranked setups, flagging A+ opportunities.
- [ ] T042 Implement `src/services/backtester.py` to replay historical data, reuse live detectors, compute Sortino ratio/profit factor/drawdown, and persist results.
- [ ] T043 Implement `src/cli/main.py` (Typer or argparse) wiring subcommands, shared options, and dependency injection for services.
- [ ] T044 Implement `src/cli/detect_cmd.py` to execute live detection runs, load runtime config, and emit ranked setup reports to stdout/files.
- [ ] T045 Implement `src/cli/backtest_cmd.py` to load backtest config, orchestrate backtester service, and save metrics/figures to disk.

## Phase 3.4: Polish & Validation
- [ ] T046 Execute and, if needed, refresh `specs/001-trendline-breakout/quickstart.md`, then follow it end-to-end to validate CLI flows and document any deviations.
- [ ] T047 [P] Assess performance against the 5-minute update cycle goal by profiling detector/backtester pipelines on sample data and tuning batching/cache settings as needed.
- [ ] T048 [P] Update project documentation (root README and specs/ changelog) with usage instructions, configuration notes, and summary of validated metrics.

## Dependencies
- T002 depends on T001; T003 depends on T002; T004 and T005 depend on T001.
- Test tasks (T006–T028) require setup tasks T001–T005 and should be completed before implementation tasks T029–T045.
- Model implementations (T032–T036) depend on their corresponding tests (T014–T018) and shared utilities (T029–T031).
- Service implementations (T037–T042) depend on service tests (T022–T027), models (T032–T036), and libraries (T029–T031).
- CLI tasks (T043–T045) depend on services (T037–T042) and CLI tests (T028).
- Polish tasks (T046–T048) require all prior implementation and tests to be passing.

## Parallel Execution Examples
```
# After T005 completes, you can kick off independent test authoring in parallel:
Run T006, T007, T008, T009 together (different contract files).
Run T014, T015, T016, T017, T018 concurrently for model tests.
Run T022, T023, T024, T025, T026, T027 together once shared fixtures exist.
```

## Notes
- Maintain TDD discipline: do not implement production code until its corresponding tests are red.
- Keep fixtures reusable (consider `tests/conftest.py`) to avoid duplication across integration and service tests.
- Ensure schemas and validation logic stay consistent between contracts, models, and services to satisfy FR-001 through FR-030.
