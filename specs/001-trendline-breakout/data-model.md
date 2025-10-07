# Data Model: Trendline Breakout Detection System

**Date**: 2025-10-07
**Feature**: Trendline Breakout Detection System
**Phase**: 1 (Design & Contracts)

## Overview
This document defines the core entities, their attributes, relationships, validation rules, and state transitions for the Trendline Breakout Detection System. Each entity maps directly to functional requirements from the feature specification.

---

## Entity Relationship Diagram (Textual)

```
CryptocurrencyPair (1) ---> (*) Trendline
Trendline (1) ---> (*) TouchPoint
Trendline (1) ---> (*) BreakoutEvent
BreakoutEvent (1) ---> (1) Trendline
BreakoutEvent (*) ---> (1) A+TradeSetup
SupplyDemandLevel (*) ---> (1) A+TradeSetup
CryptocurrencyPair (1) ---> (*) SupplyDemandLevel
```

---

## Entity 1: Trendline

### Description
A line connecting price highs or lows over time, representing support or resistance levels that price has historically respected.

### Attributes

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| id | UUID | Yes | Unique identifier | Auto-generated |
| pair_symbol | String | Yes | Cryptocurrency pair (e.g., "BTCUSDT") | Non-empty, valid symbol format |
| direction | Enum | Yes | "support" or "resistance" | One of: [support, resistance] |
| touch_points | List[TouchPoint] | Yes | Price points touching the trendline | Length >= 3 (FR-001) |
| timeframe | Enum | Yes | Chart timeframe | One of: [1h, 4h, daily, weekly] |
| slope | Float | Yes | Line slope (price change per time unit) | Non-zero |
| intercept | Float | Yes | Y-intercept for line equation | Any float |
| created_at | DateTime | Yes | When trendline first detected | ISO 8601 format |
| last_updated | DateTime | Yes | Last recalculation timestamp | ISO 8601, >= created_at |
| is_valid | Boolean | Yes | Whether trendline still active | Default: true |
| r_squared | Float | Yes | Fit quality (0.0 to 1.0) | 0.0 <= value <= 1.0 |
| quality_score | Float | Yes | Overall ranking score | 0.0 <= value <= 100.0 |

### Relationships
- **Belongs to**: CryptocurrencyPair (many-to-one)
- **Contains**: TouchPoint collection (one-to-many)
- **Referenced by**: BreakoutEvent (one-to-many)

### State Transitions

```
[New Detection] --> VALID (is_valid=true)
    |
    v
[Price breaks] --> BROKEN (is_valid=false, final state)
    |
    v
[Time decay] --> EXPIRED (is_valid=false, no touches in 30+ days)
    |
    v
[Revalidation] --> VALID (new touch point confirms)
```

### Validation Rules (from FR-001 to FR-007)
- **FR-001**: Minimum 3 touch points required
- **FR-002**: Touch point count stored and queryable
- **FR-003**: Direction must be support or resistance
- **FR-004**: Last_updated timestamp updated on new price data
- **FR-005**: Quality score calculated from: touch count (40%), timeframe weight (30%), touch distribution (20%), slope/duration (10%)
- **FR-006**: Trendlines with 3+ touches ranked higher (quality_score boost)
- **FR-007**: Timeframe weighting: weekly/daily (high priority), 4h/1h (standard priority)

### Derived Attributes
- **touch_point_count**: `len(touch_points)`
- **touch_distribution_score**: Standard deviation of touch point timestamps (normalized)
- **age_days**: `(now - created_at).days`

---

## Entity 2: TouchPoint

### Description
A specific price point where the asset price touches or comes very close to an established trendline, validating the trendline's significance.

### Attributes

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| id | UUID | Yes | Unique identifier | Auto-generated |
| trendline_id | UUID | Yes | Parent trendline reference | Must exist in Trendline table |
| timestamp | DateTime | Yes | When touch occurred | ISO 8601 format |
| price | Decimal | Yes | Actual price at touch | > 0 |
| distance_from_line | Float | Yes | Distance from trendline (%) | -5.0 <= value <= 5.0 |
| is_confirmed | Boolean | Yes | Whether touch validated | Default: false |
| candle_type | Enum | Yes | "wick" or "body" | One of: [wick, body] |

### Relationships
- **Belongs to**: Trendline (many-to-one)

### Validation Rules
- **Distance tolerance**: Touch confirmed if |distance_from_line| <= 1.0% (configurable)
- **Temporal ordering**: Timestamps must increase monotonically within same trendline
- **Minimum spacing**: Touch points should be >= 5 candles apart on same timeframe

### Derived Attributes
- **candles_since_previous**: Time difference from previous touch point in candle units

---

## Entity 3: BreakoutEvent

### Description
An occurrence where price crosses and closes beyond a trendline, indicating a potential change in trend or continuation signal.

### Attributes

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| id | UUID | Yes | Unique identifier | Auto-generated |
| trendline_id | UUID | Yes | Which trendline broke | Must exist in Trendline table |
| timestamp | DateTime | Yes | Breakout candle close time | ISO 8601 format |
| price | Decimal | Yes | Close price of breakout candle | > 0 |
| direction | Enum | Yes | "upward" or "downward" | One of: [upward, downward] |
| confirmation_stage | Integer | Yes | Current stage (1-3) | 1 <= value <= 3 |
| initial_break_timestamp | DateTime | Yes | Stage 1 timestamp | ISO 8601 format |
| retest_timestamp | DateTime | No | Stage 2 timestamp (if reached) | ISO 8601, > initial_break_timestamp |
| rejection_timestamp | DateTime | No | Stage 3 timestamp (if reached) | ISO 8601, > retest_timestamp |
| breakout_volume | Float | Yes | Volume on breakout candle | >= 0 |
| average_volume | Float | Yes | 20-period average volume | > 0 |
| volume_ratio | Float | Yes | breakout_volume / average_volume | >= 0 |
| subsequent_movement | Decimal | No | Price change after breakout (%) | Any float |
| subsequent_high | Decimal | No | Highest price after breakout | >= price |
| subsequent_low | Decimal | No | Lowest price after breakout | <= price |

### Relationships
- **References**: Trendline (many-to-one)
- **Part of**: A+TradeSetup (many-to-one, optional)

### State Transitions (FR-008, FR-011)

```
[Price closes beyond line] --> STAGE_1 (confirmation_stage=1)
    |
    v
[Price retests line] --> STAGE_2 (confirmation_stage=2)
    |
    v
[Retest rejected] --> STAGE_3 (confirmation_stage=3, CONFIRMED)
    |
    v
[No retest in window] --> EXPIRED (failed confirmation)
```

### Validation Rules (from FR-008 to FR-011)
- **FR-008**: Three-stage confirmation tracked via confirmation_stage field
- **FR-009**: All timestamp, price, and trendline details recorded
- **FR-010**: Direction must align with trendline type (resistance→upward, support→downward)
- **FR-011**: Confirmation status tracked through stage progression

### Business Rules
- **Retest window**: 5-15 candles after initial break (configurable per timeframe)
- **Rejection criteria**: Price must move >= 1% away from trendline after retest
- **Volume threshold**: volume_ratio >= 1.2 for confirmed breakout

---

## Entity 4: SupplyDemandLevel

### Description
A price zone where historical buying or selling pressure was significant, representing areas of institutional interest.

### Attributes

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| id | UUID | Yes | Unique identifier | Auto-generated |
| pair_symbol | String | Yes | Cryptocurrency pair | Non-empty, valid symbol |
| price_high | Decimal | Yes | Upper bound of zone | > 0 |
| price_low | Decimal | Yes | Lower bound of zone | > 0, < price_high |
| strength | Float | Yes | Zone strength score (0-100) | 0.0 <= value <= 100.0 |
| formation_type | Enum | Yes | "supply" or "demand" | One of: [supply, demand] |
| touch_count | Integer | Yes | Times price touched zone | >= 3 |
| timeframe | Enum | Yes | Timeframe detected on | One of: [1h, 4h, daily, weekly] |
| created_at | DateTime | Yes | Zone first identified | ISO 8601 format |
| is_active | Boolean | Yes | Whether zone still valid | Default: true |
| invalidation_timestamp | DateTime | No | When zone broke | ISO 8601, > created_at |

### Relationships
- **Belongs to**: CryptocurrencyPair (many-to-one)
- **Referenced by**: A+TradeSetup (many-to-many)

### State Transitions

```
[Consolidation detected] --> ACTIVE (is_active=true)
    |
    v
[Price breaks through] --> INVALIDATED (is_active=false)
    |
    v
[Multiple rejections] --> STRENGTHENED (strength score increases)
```

### Validation Rules (from FR-012 to FR-014)
- **FR-012**: Detected from historical price consolidations
- **FR-013**: Alignment checked with breakout direction
- **FR-014**: Within 2% price distance to qualify as aligned

### Business Rules
- **Zone width**: (price_high - price_low) / price_low should be 0.5% to 3%
- **Strength calculation**: (touch_count × 0.5) + (age_in_days × 0.1) + (timeframe_weight × 0.4)
- **Alignment check**: Zone center within 2% of breakout price

---

## Entity 5: A+TradeSetup

### Description
A high-confidence trading opportunity that meets multiple confirmation criteria, representing the highest quality breakout signals.

### Attributes

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| id | UUID | Yes | Unique identifier | Auto-generated |
| trendline_id | UUID | Yes | Primary trendline that broke | Must exist |
| breakout_id | UUID | Yes | Specific breakout event | Must exist |
| pair_symbol | String | Yes | Cryptocurrency pair | Non-empty, valid symbol |
| timeframe | Enum | Yes | Primary timeframe | One of: [1h, 4h, daily, weekly] |
| quality_score | Float | Yes | Trendline quality (0-100) | 0.0 <= value <= 100.0 |
| sd_alignment | Boolean | Yes | Supply/demand aligned | true/false |
| sd_level_ids | List[UUID] | No | Aligned SD zones | Valid UUIDs |
| htf_alignment | Boolean | Yes | Higher timeframe aligned | true/false |
| volume_confirmed | Boolean | Yes | Volume spike present | true/false |
| confluence_score | Float | Yes | Overall confluence (0-100) | 0.0 <= value <= 100.0 |
| confidence_score | Float | Yes | Final ranking score (0-100) | 0.0 <= value <= 100.0 |
| confirmation_factors | List[String] | Yes | List of met criteria | Non-empty list |
| detected_at | DateTime | Yes | When setup identified | ISO 8601 format |
| rank | Integer | Yes | Relative rank among setups | >= 1 |

### Relationships
- **References**: Trendline (many-to-one)
- **References**: BreakoutEvent (one-to-one)
- **References**: SupplyDemandLevel (many-to-many via sd_level_ids)

### Validation Rules (from FR-015 to FR-018)
- **FR-015**: Multiple confirmation criteria must be met
- **FR-016**: Required minimums: quality_score >= 60 (3+ touches), sd_alignment = true
- **FR-017**: Additional requirements: htf_alignment = true, volume_confirmed = true
- **FR-018**: Ranked by confluence_score (primary), then recency (secondary)

### Business Rules
- **Minimum criteria**: All four Boolean flags must be true to qualify as A+ setup
- **Confluence calculation**:
  ```
  confluence_score = (quality_score × 0.3) +
                     (sd_alignment × 20) +
                     (htf_alignment × 30) +
                     (volume_confirmed × 20)
  ```
- **Confidence calculation**:
  ```
  confidence_score = (confluence_score × 0.7) +
                     (recency_score × 0.3)
  recency_score = 100 - min(hours_since_detection, 100)
  ```
- **Confirmation factors**: ["3+ touches", "SD aligned", "HTF aligned", "Volume spike", ...]

---

## Entity 6: CryptocurrencyPair

### Description
A trading pair being analyzed by the system, tracked for active trendlines and recent breakout events.

### Attributes

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| symbol | String | Yes | Trading pair symbol | Primary key, e.g., "BTCUSDT" |
| base_asset | String | Yes | Base currency | e.g., "BTC" |
| quote_asset | String | Yes | Quote currency | e.g., "USDT" |
| market_cap_rank | Integer | Yes | Current ranking by market cap | 1 <= value <= 50 |
| current_price | Decimal | Yes | Latest price | > 0 |
| last_price_update | DateTime | Yes | Price data timestamp | ISO 8601 format |
| is_monitored | Boolean | Yes | Active monitoring status | Default: true |
| added_at | DateTime | Yes | When pair added to system | ISO 8601 format |
| removed_at | DateTime | No | When monitoring stopped | ISO 8601, > added_at |

### Relationships
- **Contains**: Trendline collection (one-to-many)
- **Contains**: SupplyDemandLevel collection (one-to-many)

### Derived Attributes (not stored)
- **active_trendlines**: List of trendlines where is_valid=true
- **recent_breakouts**: List of breakouts from last 7 days
- **active_a_plus_setups**: Current A+ setups for this pair

### Validation Rules (from FR-019 to FR-022)
- **FR-019**: Only pairs in top 50 by market cap
- **FR-020**: Price data must be fetchable from API
- **FR-021**: Market cap rank updated weekly
- **FR-022**: Pair monitoring stability (don't churn in/out rapidly)

### Business Rules
- **Stability buffer**: Keep pairs until they drop below rank 60 (hysteresis)
- **Monitoring pause**: If price data fails for 24+ hours, set is_monitored=false
- **Reactivation**: Can reactivate if pair returns to top 50

---

## Cross-Entity Validation Rules

### Referential Integrity
1. **Trendline → CryptocurrencyPair**: trendline.pair_symbol must exist in CryptocurrencyPair
2. **TouchPoint → Trendline**: touch_point.trendline_id must be valid
3. **BreakoutEvent → Trendline**: breakout.trendline_id must be valid
4. **A+TradeSetup → BreakoutEvent**: setup.breakout_id must be valid
5. **A+TradeSetup → SupplyDemandLevel**: All IDs in sd_level_ids must exist

### Consistency Rules
1. **Breakout direction alignment**:
   - If trendline.direction = "resistance", breakout.direction must be "upward"
   - If trendline.direction = "support", breakout.direction must be "downward"

2. **Timeframe consistency**:
   - TouchPoints must have same timeframe as parent Trendline
   - A+TradeSetup timeframe should match primary Trendline timeframe

3. **Temporal ordering**:
   - Breakout timestamps: initial_break < retest < rejection
   - Trendline: created_at <= last_updated
   - TouchPoints within trendline must have increasing timestamps

### Business Logic Constraints
1. **A+ Setup qualification**: Cannot create A+TradeSetup if:
   - Trendline has < 3 touch points
   - Breakout confirmation_stage < 3
   - No SD alignment found

2. **Trendline invalidation**: Must set is_valid=false when:
   - Breakout with confirmation_stage=3 occurs
   - No new touch points for 30+ days
   - R-squared drops below 0.7 threshold

---

## Data Retention & Archival (from FR-030)

### Retention Policy
- **Indefinite retention**: All trendlines, breakouts, and trade setups kept permanently
- **Purpose**: Long-term backtesting and pattern analysis
- **Storage optimization**: Archive old data to separate tables after 1 year

### Archive Strategy
- **Active data**: Last 12 months in primary tables
- **Historical data**: Older than 12 months in archive tables
- **Query access**: Unified views span both active and archived data

---

## Database Schema Notes

### Indexing Strategy
- **Primary keys**: All UUIDs indexed
- **Foreign keys**: All relationship fields indexed
- **Query optimization**:
  - Index on (pair_symbol, timeframe, is_valid) for trendline queries
  - Index on (confirmation_stage, timestamp) for breakout queries
  - Index on (confidence_score, detected_at) for A+ setup ranking

### Partitioning Considerations
- **Partition by timeframe**: Separate tables/partitions per timeframe if scale increases
- **Partition by date**: Archive partitions by year for old data

---

## Validation Summary Checklist

- [X] All entities from spec Key Entities section defined
- [X] Functional requirements (FR-001 to FR-030) mapped to validation rules
- [X] Relationships between entities documented
- [X] State transitions defined where applicable
- [X] Derived attributes identified separately
- [X] Cross-entity validation rules specified
- [X] Data retention policy documented (FR-030)
- [X] No implementation details (database-agnostic)

---

**Status**: Data model complete, ready for contract generation
**Next Step**: Generate API contracts in /contracts/ directory
