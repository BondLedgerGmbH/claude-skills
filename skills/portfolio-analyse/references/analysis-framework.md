<!-- analysis-framework.md
     Loaded by impact-analyst and recommendation-engine subagents.
     Provides the "how": behavioural constraints (voice, tone,
     anti-patterns), position sizing methodology, and the step-by-step
     analytical methodology.

     Subagent mapping:
     - Step 0:   market-researcher
     - Step 0.5: opportunity-scorer
     - Steps 1-5: impact-analyst
     - Steps 6-12: recommendation-engine -->

# Analysis Framework

## Behavioral Constraints
- Never fabricate data, statistics, correlations, or causal relationships.
  If information is unavailable or uncertain, state the gap transparently.
  A clearly flagged unknown is always preferable to a confident-sounding
  guess. Use labels: [VERIFIED], [ESTIMATED], [UNCERTAIN], [NOT ASSESSED].
- Never use meta-phrases or self-referential language
  ("let me help", "I can see that", "this analysis will")
- Never summarize by default; summaries only where explicitly
  requested in a section
- Never provide unsolicited generic advice
- Always be specific and concrete; avoid vague phrasing or platitudes
- Always acknowledge uncertainty; distinguish between facts,
  assumptions, estimates, and speculation
- State opinions directly without hedging

## Position Sizing Methodology

All new position recommendations (ADD) and size adjustments must include
a calculated position size:

- **Base allocation by conviction:**
  - High conviction: 3-5% of liquid NAV
  - Medium conviction: 1-3% of liquid NAV
  - Low conviction: 0.5-1% of liquid NAV

- **Volatility modifier:** Halve the base allocation for high-volatility
  instruments (crypto, small-cap <$2B, leveraged, frontier market equity).
  Full base for low-volatility instruments (large-cap DM, IG bonds, money market).

- **Concentration caps:**
  - No single new position >5% of liquid NAV
  - No single sector >30% cumulative exposure after addition

- **Liquid NAV:** Pre-computed in the portfolio-summary JSON as
  `combined.liquid_nav`. This includes IB NAV + off-platform liquid assets
  (precious metals at spot, crypto at spot, private equity options at FMV).
  Real estate is excluded (illiquid). Use this value directly; do not
  calculate manually from investor-context.md.

State the formula and resulting size explicitly in each recommendation.

## Analysis Methodology

### 0. Global Market Research (market-researcher subagent)
Execute the seven-section research methodology defined in the
market-researcher agent: macro data collection with freshness labels,
regime classification (probability-weighted), credit cycle positioning,
geopolitical risk overlay, regional/sector analysis, micro/tactical,
and synthesis. Includes data quality validation gate.

### 0.5. Opportunity Scoring (opportunity-scorer subagent)
Using the regime classification and credit cycle from Step 0:
identify historical comparable periods, score opportunities by
conviction and regime fit, identify geopolitical tradeable expressions
and regional divergence pair trades. If data quality is LOW-CONFIDENCE,
cap maximum conviction at Medium.

### 1. Portfolio Snapshot
- Combined NAV across all accounts (IB + off-platform). The portfolio-summary
  JSON contains both IB and off-platform positions in a single `positions`
  array. Off-platform positions have `account: "off_platform"` and
  `source: "manual"`. Real estate positions have `liquidity: "illiquid"`.

**Asset class taxonomy.** Every position must be classified into one of
these standard asset classes and sub-classes:

| Asset Class | Sub-classes | What maps here |
|-------------|-------------|----------------|
| Equities | Single stocks, Equity ETFs | Individual shares (AMZN, MSFT, ...), equity ETFs (VYM, VEA, VWO, VB, VIGI, LIT, TAN, ...) |
| Fixed Income | Treasuries, Bond ETFs | T-bill ETFs (SGOV), bond ETFs, any future bond holdings |
| Cash & Cash Equivalents | Money market funds, Uninvested cash | Money market ETFs (XEON, CSH2), uninvested cash balances from `balances.{account}.cash` |
| Commodities | Physical gold, Physical silver | Off-platform precious metals |
| Cryptocurrency | BTC, other | Off-platform crypto holdings |
| Private Equity | Stock options | Off-platform private equity (private equity options, etc.) |
| Real Estate *(illiquid)* | Primary residence, Investment property | Off-platform real estate |

**Cash & Cash Equivalents**: this class equals the sum of uninvested cash
balances from the portfolio JSON (`balances.{account}.cash` for each account)
plus money market fund positions (XEON, CSH2, or similar). Do not derive
cash by subtracting positions from NAV. Use the values directly from the JSON.

**Dual denominator.** All allocation tables show two percentage columns:
- `% Liquid NAV` = value / `combined.liquid_nav`. Used for investment
  recommendations and position sizing. Real estate shows "--" (excluded).
- `% Total NAV` = value / `combined.total_wealth`. Used for wealth overview.
  All asset classes included.

Allocation tables use the hierarchical format defined in output-template.md:
parent rows (bold, showing sub-class sums) and indented sub-class rows.

- Allocation by: asset class (hierarchical), sector, geography, currency.
- Per-account breakdown (for tax-aware recommendations): include off_platform
  as a separate account alongside IB accounts.
- Concentration flags: pre-computed in the JSON on the full portfolio
  (IB + off-platform). Report as provided.
- Margin assessment: the portfolio data contains `maintenance_margin_req`
  and `margin_borrowed`. `maintenance_margin_req` is the equity IB requires
  to hold current positions (always non-zero for margin accounts with
  positions). `margin_borrowed` is actual borrowed funds (negative cash
  balance). Only report margin as a risk if `margin_borrowed` > 0.
  Do not confuse the maintenance requirement with actual borrowing.

### 2. Correlation and Cluster Analysis
- Identify groups of holdings likely to move together in drawdowns.
  Include off-platform assets in cluster identification:
  - Physical precious metals form a commodity/hedge cluster
    (correlated with inflation expectations, inversely correlated with
    real yields and risk appetite)
  - Bitcoin forms a crypto/volatility cluster (correlated with risk
    appetite and liquidity conditions, partially correlated with tech)
  - private equity options have fintech/crypto sector correlation
- Flag indirect exposures (e.g., ETFs with heavy NVDA weighting,
  cloud providers dependent on AI capex)
- Assess USD concentration across all holdings including off-platform
  (precious metals quoted in USD, Bitcoin in USD, private equity in USD)

### 2.5. New Opportunity Overlap Assessment
For each opportunity from the opportunity-scorer, check against existing
holdings for direct overlap (same ticker), sector/theme overlap, and
correlation cluster overlap. Assess each as PROCEED / CAUTION / REDUNDANT.
Calculate prospective concentration if all PROCEED/CAUTION opportunities
were added.

### 3. Thesis/Event Impact Assessment
For each relevant position or cluster:
- Direct impact: is this position directly affected?
- Indirect impact: second-order effects
  (supply chain, customer base, sector contagion)
- Magnitude: high/medium/low
- Direction: positive/negative/neutral
- Confidence: how strong is the causal link?
- Timeframe: immediate, 3-6 months, 12+ months

### 4. Currency Exposure Analysis
- Total USD exposure (direct + indirect). Off-platform assets are
  USD-denominated in the portfolio JSON (precious metals and crypto
  are globally priced in USD, private equity is a US company). Include them
  in USD totals. Real estate is in local currency (CHF).
- CHF, EUR, and other currency exposures
- Recommended target allocation aligned with USD thesis
- Hedging mechanisms if appropriate

### 5. Risk Assessment
Evaluate exposure across five dimensions:
- Micro risks: company-specific (earnings, competitive, management)
- Macro risks: interest rate sensitivity, inflation, economic cycle
- Geopolitical risks: regional concentration, supply chain, regulatory
- Valuation risk: elevated multiples, sentiment vulnerability
- Currency/sovereign risk: USD depreciation, US fiscal policy,
  counterparty exposure to US financial system

### 6. Recommendations
For each recommendation:
- Source tag: [IMPACT-DRIVEN] or [OPPORTUNITY-SCORER]
- Action: [TRIM], [EXIT], [ADD], [REBALANCE], [HEDGE]
- Strategic intent: [RISK MITIGATION], [GROWTH OPTIMIZATION], [USD HEDGE]
- Instrument: specific ticker, exchange, currency
- Target account: specify account1, account2, or off_platform, using the
  account names from investor-context.md and ib-connect MCP configuration.
  Off-platform recommendations are advisory (user must execute outside IB).
  Mark off-platform actions with a note: "Off-platform: manual execution required."
- Position size: per Position Sizing Methodology (conviction, base %,
  volatility modifier, resulting size)
- Rationale: why this action, referencing the thesis/event or opportunity
- Proceeds deployment (required for TRIM, EXIT, REBALANCE): where the
  freed capital goes. Must be specific. Never leave proceeds unaddressed.
  For off-platform TRIM/EXIT, note that proceeds may not be immediately
  deployable to IB (transfer time, custody logistics).
- Tax note:
  - Personal account: no capital gains tax; flag dividend withholding if relevant
  - Corporate account: corporate tax impact; participation exemption eligibility
  - Off-platform: apply personal tax treatment (local tax rules per investor-context.md)
    unless the asset is held in a corporate structure
- Tradeoff: what you give up by taking this action
- Priority: High / Medium / Low

### 7. Steelman Check
For the top 3 recommendations:
- What is the strongest case against this recommendation?
- Under what conditions would this be the wrong move?
- What signal would invalidate the thesis behind it?

### 8. Stress Testing
Define 2-3 stress scenarios based on regime-shift risks. For each:
position-level drawdown estimates, portfolio-level drawdown, top
contributors to loss and protection. Flag if any scenario breaches
escalation thresholds (>25% drawdown or >5% single-position contribution).

### 9. Staged Deployment Plan
For ADD/REBALANCE recommendations above 1% liquid NAV: deploy over
2-6 weeks in tranches with entry conditions and abort triggers.

### 10. Watchlist
Flag positions or macro indicators to monitor over next 6-12 months:
- Earnings dates or catalysts for held positions
- Policy developments (Fed, ECB, SNB, fiscal)
- Signals that would cause revision of standing theses

### 11. Monitoring Framework
Three tiers: monthly macro review (regime + credit cycle recheck),
weekly position review (per-position thesis validation), and
regime shift signals (3-5 specific data points with thresholds).

### 12. Escalation Flags
Flag threshold breaches for orchestrator: stress test breach,
position/sector concentration, correlation cluster, or data quality
issues. State which upstream stage to re-run and with what constraint.

### 13. Comparison Analysis (Mode 4 only)
When two inputs are provided:
- Source A summary: core argument in one paragraph
- Source B summary: core argument in one paragraph
- Agreement matrix: claims both sources support, positions that
  benefit under both scenarios
- Conflict matrix: where the sources disagree, positions that
  are exposed differently per scenario
- Positioning assessment: current portfolio risk/reward given
  the disagreement; which scenario would hurt more
- Hedged recommendations: actions that reduce risk under both
  scenarios, plus conditional recommendations tied to specific outcomes
- Decision triggers: signals that would confirm one source over
  the other, enabling decisive action
