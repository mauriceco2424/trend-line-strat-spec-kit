# Technical Research: Trendline Breakout Detection System

**Date**: 2025-10-07
**Feature**: Trendline Breakout Detection System
**Phase**: 0 (Research & Technical Decisions)

## Overview
This document captures the technical research and decisions made for implementing the Trendline Breakout Detection System. Each decision includes the rationale and alternatives considered.

---

## Research Area 1: Trendline Detection Algorithms

### Decision
**Pivot-based trendline detection using local extrema identification**

Implementation approach:
- Identify swing highs and swing lows using rolling window analysis
- Connect pivots with minimum 3 touch points within tolerance threshold
- Use linear regression to refine trendline slope and validate fit quality
- Calculate R-squared coefficient to measure trendline strength

### Rationale
- Pivot-based methods align with how human traders identify trendlines
- Produces interpretable results that match visual chart analysis
- Computationally efficient for real-time analysis across 50 pairs
- Allows for configurable tolerance thresholds (e.g., 0.5-1% price distance)
- Well-suited for cryptocurrency markets with high volatility

### Alternatives Considered
1. **Pure Linear Regression**: Fit lines to all price points in window
   - Rejected: Too sensitive to outliers, doesn't match trader intuition
   - Produces mathematically optimal lines that traders wouldn't draw

2. **Hough Transform**: Computer vision technique for line detection
   - Rejected: Overly complex for financial data, harder to interpret
   - Better suited for image processing than time series analysis

3. **Support/Resistance Clustering**: Group prices into horizontal zones
   - Rejected: Doesn't capture diagonal trendlines, only horizontal S/R levels
   - Will use this separately for supply/demand zones

### Implementation Notes
- Use scipy.signal.find_peaks for pivot identification
- Store pivot indices for touch point tracking
- Minimum 3 pivots required per trendline (FR-001)
- Recalculate on each new candle close (FR-004)

---

## Research Area 2: Breakout Confirmation Methods

### Decision
**Three-stage confirmation process with volume validation**

Stages:
1. **Initial Break**: Candle closes beyond trendline (body close, not wick)
2. **Retest**: Price returns to trendline within N candles (configurable: 5-15 candles)
3. **Rejection**: Price bounces away from retest (minimum 1% move in breakout direction)

Volume confirmation:
- Volume on breakout candle must exceed 20-period average volume
- Higher timeframe trend alignment checked (daily/weekly for 4h breakouts)

### Rationale
- Three-stage process filters false breakouts (reduces ~60-70% of noise)
- Body close requirement prevents wick fakeouts
- Retest confirmation validates support/resistance flip
- Volume requirement ensures institutional participation
- Matches professional trader methodology from spec clarifications

### Alternatives Considered
1. **Single candle close confirmation**: Too many false signals
   - Rejected: High false positive rate in volatile crypto markets

2. **Percentage move requirement**: Require 2-3% move beyond trendline
   - Rejected: Misses valid breakouts on higher timeframes with tighter stops
   - May implement as optional filter for A+ setups

3. **Fixed time period**: Must hold beyond trendline for X hours
   - Rejected: Doesn't adapt to different timeframes or market conditions
   - Our retest approach is more flexible

### Implementation Notes
- Track confirmation stage in BreakoutEvent model (1, 2, or 3)
- Store retest candle timestamp and price
- Configurable retest window per timeframe (shorter for 1h, longer for daily)
- Volume data required from price API (OHLCV format)

---

## Research Area 3: Supply/Demand Zone Detection

### Decision
**Consolidation-based zone identification with order block validation**

Approach:
- Identify consolidation areas (narrow price ranges with multiple touches)
- Classify as supply (resistance) or demand (support) based on breakout direction
- Measure zone strength by touch count and age
- Validate zones using order block patterns (impulsive moves from zones)

Zone alignment criteria:
- Within 2% price distance of breakout point (FR-014)
- Same direction as breakout (demand zones for upward breaks)
- Minimum 3 touches to qualify as valid zone

### Rationale
- Consolidation zones represent areas of institutional accumulation/distribution
- Order blocks indicate large orders executed at specific price levels
- 2% threshold balances precision with realistic market behavior
- Strength scoring enables ranking of A+ setups
- Widely used in smart money concepts and institutional trading

### Alternatives Considered
1. **Volume profile analysis**: Identify high-volume price nodes
   - Rejected: Requires tick-level volume data (not available from all APIs)
   - More computationally intensive

2. **Fibonacci retracement levels**: Standard 38.2%, 50%, 61.8% levels
   - Rejected: Not data-driven, arbitrary levels not always relevant
   - May add as supplementary filter later

3. **Round number psychology**: Focus on .00, .50 price levels
   - Rejected: Less relevant for lower-priced cryptocurrencies
   - Better suited for major pairs only

### Implementation Notes
- Store zones with price_high, price_low range
- Calculate strength score: (touch_count × 0.5) + (age_in_days × 0.1)
- Check alignment in trade_ranker service
- Update zone status when price breaks through (invalidate zone)

---

## Research Area 4: Cryptocurrency Price Data API

### Decision
**Binance API as primary data source with CoinGecko for market cap rankings**

Binance API:
- Endpoint: `GET /api/v3/klines`
- Parameters: symbol, interval (1h/4h/1d/1w), limit (up to 1000 candles)
- Rate limit: 1200 requests/minute (weight-based)
- Data format: [timestamp, open, high, low, close, volume, ...]

CoinGecko API:
- Endpoint: `GET /api/v3/coins/markets`
- Used for top 50 market cap rankings (FR-019, FR-021)
- Rate limit: 10-50 calls/minute (free tier)
- Weekly update schedule sufficient

### Rationale
- Binance has highest liquidity and most comprehensive cryptocurrency coverage
- Free API access with generous rate limits
- Historical data available back 3+ years
- Reliable uptime (99.9%+)
- CoinGecko provides accurate market cap data for pair selection
- Both APIs well-documented with Python client libraries available

### Alternatives Considered
1. **CryptoCompare API**: Historical data provider
   - Rejected: More expensive, rate limits restrictive on free tier
   - Binance data quality superior for major pairs

2. **Coinbase Pro API**: Reputable exchange
   - Rejected: Limited cryptocurrency coverage (~50-100 pairs vs Binance 500+)
   - Fewer trading pairs for top 50 coverage

3. **Alpha Vantage**: Financial data provider
   - Rejected: Crypto coverage limited, slower update frequency
   - Better suited for stock/forex analysis

### Implementation Notes
- Implement request caching to stay within rate limits
- Store API responses in local SQLite/files to minimize calls
- Handle API errors gracefully (retry logic, fallback to cache)
- Update price data on configurable schedule (every 15-60 minutes)
- Use python-binance library for API interactions

---

## Research Area 5: Performance Metrics Calculation

### Decision
**Three primary metrics: Sortino Ratio, Profit Factor, Maximum Drawdown**

Sortino Ratio:
- Formula: (Mean Return - Risk-Free Rate) / Downside Deviation
- Uses only negative volatility (downside risk)
- Risk-free rate: 0% (crypto market assumption)
- Annualization factor: sqrt(365) for daily returns

Profit Factor:
- Formula: Gross Profits / Gross Losses
- Values > 1.0 indicate profitable strategy
- Industry benchmark: 1.5+ considered good, 2.0+ excellent

Maximum Drawdown:
- Formula: (Trough - Peak) / Peak
- Largest peak-to-trough decline in equity curve
- Critical for risk management and position sizing

Adaptive time horizons (FR-024):
- 1h timeframe: 24-hour measurement window
- 4h timeframe: 7-day measurement window
- Daily timeframe: 30-day measurement window
- Weekly timeframe: 90-day measurement window

### Rationale
- Sortino ratio preferred over Sharpe (focuses on downside risk, not total volatility)
- Profit factor simple and intuitive for traders
- Maximum drawdown essential for capital preservation
- Adaptive horizons match typical hold periods for each timeframe
- All three metrics complement each other (risk-adjusted returns + profitability + risk)

### Alternatives Considered
1. **Sharpe Ratio**: More common risk-adjusted metric
   - Rejected: Penalizes upside volatility (undesirable in trading)
   - Sortino ratio better suited for asymmetric return distributions

2. **Win Rate**: Percentage of winning trades
   - Rejected: Can be misleading (high win rate with large losses = unprofitable)
   - Will calculate as supplementary metric but not primary

3. **Calmar Ratio**: Return / Maximum Drawdown
   - Rejected: Similar to Sortino but less standard in crypto trading
   - May add later as additional metric

### Implementation Notes
- Calculate metrics in backtester service
- Store results per breakout in database
- Generate aggregate statistics across all breakouts
- Use pandas for efficient rolling calculations
- Plot equity curves for visual validation

---

## Research Area 6: Multi-Timeframe Analysis Patterns

### Decision
**Top-down timeframe confluence with higher timeframe filter**

Approach:
- Analyze all timeframes independently (1h, 4h, daily, weekly)
- Apply higher timeframe bias as filter for lower timeframe trades
- Rank setups based on timeframe alignment strength
- Weight system: Weekly = 4x, Daily = 3x, 4h = 2x, 1h = 1x

Confluence patterns:
- **Strong confluence**: Breakout on 4h + daily trendline aligned
- **Extreme confluence**: Breakout on 1h + 4h + daily all aligned
- A+ setups require at minimum 4h + daily alignment (FR-017)

### Rationale
- Higher timeframes more reliable (larger participant base, less noise)
- Top-down analysis matches institutional trading methodology
- Confluence scoring enables objective setup ranking
- Weighting system prevents over-optimization on 1h noise
- Aligns with professional trader best practices

### Alternatives Considered
1. **Single timeframe analysis**: Focus only on daily charts
   - Rejected: Misses early entries on lower timeframes
   - Reduces trade frequency significantly

2. **Equal timeframe weighting**: All timeframes weighted equally
   - Rejected: Gives too much importance to noisy 1h signals
   - Doesn't reflect market structure reality

3. **Dynamic timeframe selection**: Adapt based on volatility
   - Rejected: Adds complexity without clear benefit
   - Harder to backtest consistently (FR-025)

### Implementation Notes
- Store timeframe in Trendline model using enum
- Calculate confluence score in trade_ranker service
- Check higher timeframe trend direction before flagging A+ setups
- Cache higher timeframe data to reduce API calls

---

## Technology Stack Summary

### Core Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| pandas | 2.1+ | Time series data manipulation, OHLCV handling |
| numpy | 1.24+ | Numerical computations, array operations |
| scipy | 1.11+ | Signal processing (find_peaks), statistical functions |
| requests | 2.31+ | HTTP client for API calls |
| python-binance | 1.0+ | Binance API wrapper |

### Testing & Quality
| Library | Version | Purpose |
|---------|---------|---------|
| pytest | 7.4+ | Test framework |
| pytest-cov | 4.1+ | Coverage reporting |
| jsonschema | 4.19+ | Contract validation |

### Data Storage
| Technology | Purpose |
|------------|---------|
| SQLite 3 | Trendline/breakout persistence |
| Parquet | Price data caching (via pandas) |

### Development Tools
| Tool | Purpose |
|------|---------|
| black | Code formatting |
| ruff | Linting |
| mypy | Type checking |

---

## Open Questions & Assumptions

### Assumptions Made
1. **API Availability**: Binance API will remain free and available
   - Mitigation: Design abstraction layer to swap data providers

2. **Market Cap Data**: Top 50 rankings won't change drastically week-to-week
   - Mitigation: Weekly update cycle with stability buffer (keep pairs in top 60)

3. **Computational Resources**: Single-machine deployment sufficient
   - Validation: 50 pairs × 4 timeframes × 1000 candles = ~200k data points (manageable)

### Deferred Decisions
1. **Real-time vs Batch Processing**: Initial implementation batch mode (every 15-60 min)
   - Can add WebSocket real-time streaming later if needed

2. **Notification System**: Email/SMS alerts for A+ setups
   - Phase 2 feature, not required for MVP

3. **Web Dashboard**: Visualization interface for detected setups
   - Nice-to-have, CLI sufficient for initial release

---

## Research Validation Checklist

- [X] All NEEDS CLARIFICATION from Technical Context resolved
- [X] Each decision has clear rationale documented
- [X] Alternatives considered and rejection reasons provided
- [X] Implementation notes included for each area
- [X] Technology stack versions specified
- [X] Assumptions and risks identified
- [X] No HOW implementation details (focus on WHAT/WHY)

---

**Status**: Research complete, ready for Phase 1 design
**Next Step**: Generate data-model.md and API contracts
