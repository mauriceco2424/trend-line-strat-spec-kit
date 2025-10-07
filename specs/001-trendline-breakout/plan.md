# Implementation Plan: Trendline Breakout Detection System

**Branch**: `001-trendline-breakout` | **Date**: 2025-10-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-trendline-breakout/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path ✓
   → Spec loaded from C:/bitcoin_trading/trend_line_strat/specs/001-trendline-breakout/spec.md
2. Fill Technical Context (scan for NEEDS CLARIFICATION) ✓
   → Detect Project Type: single (Python trading system)
   → Set Structure Decision: Single project with src/ and tests/
3. Fill the Constitution Check section based on constitution ✓
4. Evaluate Constitution Check section ✓
   → No violations found
   → Update Progress Tracking: Initial Constitution Check ✓
5. Execute Phase 0 → research.md ✓
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, CLAUDE.md ✓
7. Re-evaluate Constitution Check section ✓
   → No new violations
   → Update Progress Tracking: Post-Design Constitution Check ✓
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md) ✓
9. STOP - Ready for /tasks command ✓
```

**IMPORTANT**: The /plan command STOPS at step 8. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
The Trendline Breakout Detection System is a cryptocurrency trading analysis tool that automatically detects and ranks trendlines across multiple timeframes (1h, 4h, daily, weekly), identifies high-quality breakout events through a three-stage confirmation process, integrates supply/demand levels for trade validation, and flags "A+ trade setups" based on multiple confluence factors. The system analyzes the top 50 cryptocurrencies by market cap and supports comprehensive backtesting with adaptive time horizons and sophisticated performance metrics (Sortino ratio, profit factor, maximum drawdown).

Technical approach: Python-based algorithmic trading system using NumPy/pandas for price data analysis, pattern detection algorithms for trendline identification, statistical methods for breakout confirmation, and persistent storage for historical trendlines and trade setups.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: pandas (time series analysis), numpy (numerical computation), requests (API calls for price data), pytest (testing framework)
**Storage**: SQLite for trendline/breakout persistence, CSV/Parquet for price data caching
**Testing**: pytest with pytest-cov for coverage, contract tests using JSON schema validation
**Target Platform**: Linux/Windows desktop, scheduled execution via cron/Task Scheduler
**Project Type**: single (Python algorithmic trading system)
**Performance Goals**: Process 50 cryptocurrency pairs across 4 timeframes within 5 minutes per update cycle
**Constraints**: API rate limits (typically 100-300 req/min for crypto exchanges), <500MB memory footprint, must handle missing/incomplete price data gracefully
**Scale/Scope**: 50 cryptocurrency pairs, 4 timeframes, 3+ years historical data, 10k+ trendlines tracked simultaneously

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: This project does not yet have a constitution.md file. The following checks are based on common software development principles that will be codified if /constitution is run:

### Simplicity Check
- ✓ **Single project structure**: Trading system as one cohesive library with clear modules
- ✓ **No premature abstraction**: Direct use of pandas/numpy, no custom data abstraction layers
- ✓ **Minimal dependencies**: Core scientific computing stack only (pandas, numpy, requests, pytest)

### Test-First Check
- ✓ **TDD workflow planned**: Contract tests → Integration tests → Implementation
- ✓ **Test coverage targets**: >80% coverage for core detection algorithms
- ✓ **Quickstart validation**: End-to-end test scenario derived from user stories

### Integration-First Check
- ✓ **Real data sources**: Integration tests use actual crypto API endpoints (with caching)
- ✓ **Realistic test data**: Historical price data samples covering edge cases
- ✓ **Contract validation**: API contracts validated against actual exchange responses

### Anti-Complexity Check
- ✓ **Direct implementation**: No plugin systems, no dynamic configuration frameworks
- ✓ **Clear boundaries**: Models, services, CLI layers with explicit dependencies
- ✓ **Standard patterns**: Standard Python project layout, conventional testing approaches

## Project Structure

### Documentation (this feature)
```
specs/001-trendline-breakout/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   ├── price-data-api.json
│   ├── trendline-detection.json
│   ├── breakout-detection.json
│   └── trade-ranking.json
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── models/
│   ├── trendline.py          # Trendline entity with touch points
│   ├── breakout.py           # Breakout event entity
│   ├── supply_demand.py      # Supply/Demand level entity
│   ├── trade_setup.py        # A+ trade setup entity
│   └── crypto_pair.py        # Cryptocurrency pair entity
├── services/
│   ├── price_fetcher.py      # Fetch price data from exchanges
│   ├── trendline_detector.py # Detect and rank trendlines
│   ├── breakout_detector.py  # Detect and confirm breakouts
│   ├── supply_demand_detector.py # Detect supply/demand zones
│   ├── trade_ranker.py       # Rank and classify A+ setups
│   └── backtester.py         # Backtest historical performance
├── cli/
│   ├── main.py               # CLI entry point
│   ├── detect_cmd.py         # Real-time detection command
│   └── backtest_cmd.py       # Backtest command
└── lib/
    ├── data_storage.py       # SQLite persistence layer
    ├── timeframe.py          # Timeframe enumeration and utilities
    └── validators.py         # Input validation utilities

tests/
├── contract/
│   ├── test_price_api_contract.py
│   ├── test_trendline_contract.py
│   ├── test_breakout_contract.py
│   └── test_trade_ranking_contract.py
├── integration/
│   ├── test_trendline_detection_flow.py
│   ├── test_breakout_detection_flow.py
│   ├── test_a_plus_setup_flow.py
│   └── test_backtest_flow.py
└── unit/
    ├── test_trendline_model.py
    ├── test_breakout_model.py
    ├── test_supply_demand_model.py
    └── test_validators.py

data/
├── cache/                    # Cached price data
└── db/                       # SQLite databases
```

**Structure Decision**: Single project structure selected because this is a cohesive trading system where all components (data fetching, trendline detection, breakout identification, ranking) work together as one logical unit. No separate frontend/backend or microservices needed - this is a data analysis pipeline with CLI interface.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Trendline detection algorithms (linear regression vs. pivot-based approaches)
   - Breakout confirmation statistical methods (volume analysis, retest validation)
   - Supply/demand zone identification techniques (consolidation areas, order blocks)
   - Cryptocurrency price data API selection (Binance, CoinGecko, CryptoCompare)
   - Performance metric calculations (Sortino ratio formula, profit factor computation)
   - Multi-timeframe analysis patterns (higher timeframe filters)

2. **Generate and dispatch research agents**:
   ```
   Research Task 1: "Research trendline detection algorithms for financial price data"
   Research Task 2: "Find best practices for breakout confirmation in technical analysis"
   Research Task 3: "Research supply and demand zone detection methods in trading"
   Research Task 4: "Evaluate cryptocurrency price data API options (Binance, CoinGecko)"
   Research Task 5: "Research Sortino ratio and profit factor calculation methods"
   Research Task 6: "Find patterns for multi-timeframe technical analysis"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all technical decisions documented

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Trendline: id, direction (support/resistance), touch_points (list), timeframe, slope, created_at, is_valid
   - TouchPoint: timestamp, price, distance_from_line, is_confirmed
   - BreakoutEvent: id, trendline_id, timestamp, price, direction, confirmation_stage (1-3), subsequent_movement
   - SupplyDemandLevel: id, price_high, price_low, strength, formation_type, touch_count, timeframe
   - A+TradeSetup: id, trendline_id, breakout_id, quality_score, sd_alignment, confidence_score, confirmation_factors (list)
   - CryptocurrencyPair: symbol, market_cap_rank, current_price, active_trendlines (list), recent_breakouts (list), is_monitored

2. **Generate API contracts** from functional requirements:
   - Price Data API: GET /price-data/{symbol}/{timeframe} → OHLCV data
   - Trendline Detection: POST /detect-trendlines → {pair, timeframe, price_data} → trendlines
   - Breakout Detection: POST /detect-breakouts → {trendline, current_price} → breakout_event
   - Trade Ranking: POST /rank-setups → {breakouts, sd_levels} → ranked_setups
   - Output JSON schemas to `/contracts/`

3. **Generate contract tests** from contracts:
   - test_price_api_contract.py: Validate OHLCV schema, timeframe values, required fields
   - test_trendline_contract.py: Validate trendline detection input/output schemas
   - test_breakout_contract.py: Validate breakout detection schemas and confirmation stages
   - test_trade_ranking_contract.py: Validate ranking output schema with A+ classification
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Story 1 → test_trendline_detection_flow.py: Detect trendline with 3+ touches and confirm breakout
   - Story 2 → test_multi_timeframe_ranking.py: Rank breakouts across 1h, 4h, daily timeframes
   - Story 3 → test_a_plus_setup_flow.py: Identify A+ setup with SD alignment
   - Story 5 → test_backtest_flow.py: Run backtest and generate performance metrics

5. **Update agent file incrementally** (O(1) operation):
   - Run `scripts/powershell/update-agent-context.ps1 -AgentType CLAUDE`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - Add: Python 3.11+, pandas, numpy, pytest, trendline detection, breakout confirmation
   - Preserve manual additions between markers
   - Update recent changes: "Phase 1 design completed for trendline breakout system"
   - Keep under 150 lines for token efficiency
   - Output to repository root: CLAUDE.md

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- **Setup Phase** (parallel where possible):
  - Create project directory structure (src/, tests/, data/)
  - Set up Python virtual environment and install dependencies
  - Initialize SQLite database schema
  - Create base model classes and validators [P]
- **Contract Test Phase** (TDD - tests first):
  - Each contract → contract test task
  - test_price_api_contract.py [P]
  - test_trendline_contract.py [P]
  - test_breakout_contract.py [P]
  - test_trade_ranking_contract.py [P]
- **Model Creation Phase** (make tests pass):
  - Each entity → model creation task
  - Trendline model with touch points [P]
  - Breakout event model [P]
  - Supply/Demand level model [P]
  - A+ Trade setup model [P]
  - Cryptocurrency pair model [P]
- **Service Implementation Phase** (dependency order):
  - Price fetcher service (required by all)
  - Trendline detector service
  - Supply/demand detector service [P with trendline detector]
  - Breakout detector service (depends on trendline detector)
  - Trade ranker service (depends on breakout + SD detectors)
  - Backtester service (depends on all detection services)
- **Integration Test Phase** (user story validation):
  - Each user story → integration test task
  - Trendline detection with breakout flow
  - Multi-timeframe ranking flow
  - A+ setup identification flow
  - Backtest analysis flow
- **CLI Phase** (user interface):
  - Main CLI entry point with argument parsing
  - Real-time detection command
  - Backtest command with reporting
- **Polish Phase**:
  - Execute quickstart.md validation
  - Performance optimization (if needed)
  - Documentation updates

**Ordering Strategy**:
- TDD order: Contract tests → Models → Service tests → Service implementation
- Dependency order: Models before services, base services before dependent services
- Mark [P] for parallel execution (independent files/modules)
- Integration tests after all services implemented
- CLI after core logic validated

**Estimated Output**: 40-45 numbered, ordered tasks in tasks.md
- Setup: 4 tasks
- Contract tests: 4 tasks
- Models: 6 tasks
- Services: 12 tasks (6 services × 2 tasks each - test + impl)
- Integration tests: 4 tasks
- CLI: 3 tasks
- Service tests: 6 tasks
- Polish: 3 tasks

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

No violations - constitution check passed without exceptions.

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [X] Phase 0: Research complete (/plan command)
- [X] Phase 1: Design complete (/plan command)
- [X] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [X] Initial Constitution Check: PASS
- [X] Post-Design Constitution Check: PASS
- [X] All NEEDS CLARIFICATION resolved
- [X] Complexity deviations documented (none)

---
*Based on Constitution principles - Constitution file not yet created. Run /constitution to codify project principles.*
