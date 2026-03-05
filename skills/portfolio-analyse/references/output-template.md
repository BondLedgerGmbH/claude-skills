<!-- output-template.md
     Loaded by recommendation-engine subagent.
     Provides the "what": the required sections and structure for
     the final analysis MD. Every section listed here must appear
     in the output unless marked as conditional.
     The recommendation-engine incorporates content from earlier
     subagent outputs (market research, opportunity scoring, impact
     analysis) into this template structure. -->

# Output Template

## Abbreviation and Label Footnotes

Every table and paragraph that introduces an abbreviation, acronym, or
bracket label for the first time in the document must include a footnote
immediately below it defining all new terms used. The footnote block
uses a compact format:

```
> **Footnotes:** DM = Developed Markets; EM = Emerging Markets;
> [GEO] = Geopolitical tradeable expression; HY = High Yield.
```

Rules:
- Only define each term once (on first appearance). Do not repeat the
  footnote in subsequent sections.
- Group all new terms from a single table or paragraph into one footnote
  block placed directly below that table or paragraph.
- Cover ALL types of shorthand: bracket labels (e.g. `[GEO]`, `[RV]`,
  `[INTEL]`, `[USD_DET]`, `[FACT]`, `[INFERENCE]`, `[LIVE]`,
  `[ESTIMATED]`, `[IMPACT-DRIVEN]`, `[OPPORTUNITY-SCORER]`),
  financial acronyms (e.g. DM, EM, HY, IG, NAV, CAPE, DXY, OTM, ATM,
  IV, ETC, ETF, REIT, ISM, PMI, CPI, PPI, PCE, HICP, NFP, SLOOS,
  FMS, YTD, YoY, MoM, FMV, FX, EMBI, C&I, IRA), and any other
  abbreviation a reader unfamiliar with finance would not immediately
  understand.
- Well-known company tickers (MSFT, AAPL) and instrument tickers
  (SPY, QQQ) do NOT need footnotes. Account names do not need
  footnotes. Standard units (USD, EUR, CHF, oz,
  BTC) do not need footnotes.
- Thesis-derived bracket labels (e.g. `[INTEL]`, `[USD_DET]`,
  `[AI_BUBBLE]`) must be footnoted with the full thesis name from
  investor-context.md on first use.

## Required Sections

### Header
- Analysis date and time
- Mode: Thesis / YouTube Transcript / Market Scan / Comparison
- If thesis mode: one-line summary of the input thesis
- If YouTube mode: video title, channel, URL, and one-line summary of content
- If comparison mode: one-line summary of each source
- Regime classification: dominant regime and probability (from market research)
- Credit cycle phase (from market research)
- Data quality status: NORMAL or LOW-CONFIDENCE (from market research)
- Global market research: fresh or cached (if cached, show age)
- Combined IB NAV
- Liquid NAV (IB + off-platform liquid assets)
- Total Wealth (including illiquid real estate)
- Number of positions across all accounts (IB + off-platform)
- Spot prices used for off-platform valuations (gold/oz, silver/oz, BTC) with fetch timestamp

### Portfolio Snapshot

Allocation tables show two percentage columns: **% Liquid NAV** (IB +
off-platform liquid; the actionable number for position sizing and
recommendations) and **% Total NAV** (liquid + illiquid; the wealth
overview number). Off-platform positions appear alongside IB positions
in every table, not in a separate section. They are marked with account
"Off-Platform" to distinguish them from IB accounts.

#### Allocation by Asset Class

A single unified table covering all on-platform and off-platform holdings.
Use the standard asset class taxonomy with parent rows (bold) and sub-class
rows (indented). Every position must map to exactly one sub-class. Cash in
the allocation table equals the uninvested cash balance from the portfolio
JSON plus money market fund positions. Do not derive cash by subtraction.

| Asset Class | Value (USD) | % Liquid NAV | % Total NAV |
|-------------|-------------|--------------|-------------|
| **Equities** | | | |
|   Single stocks | | | |
|   Equity ETFs | | | |
| **Fixed Income** | | | |
|   Treasuries (e.g. SGOV) | | | |
|   Bond ETFs | | | |
| **Cash & Cash Equivalents** | | | |
|   Money market funds (e.g. XEON, CSH2) | | | |
|   Uninvested cash | | | |
| **Commodities** | | | |
|   Physical gold | | | |
|   Physical silver | | | |
| **Cryptocurrency** | | | |
|   BTC | | | |
| **Private Equity** | | | |
|   Stock options (e.g. [COMPANY_NAME]) | | | |
| **Real Estate** *(illiquid)* | | | |
|   Primary residence | | | |
|   Investment property | | | |
| **Total** | | 100% | 100% |

Notes on the table:
- Parent rows show the sum of their sub-classes.
- Omit sub-classes with zero holdings. Add sub-classes as needed for
  new instrument types (e.g. corporate bonds, other crypto).
- Real estate is included in Total NAV but excluded from Liquid NAV
  (show "--" in the % Liquid NAV column for real estate rows).
- Spot prices used for off-platform valuations (gold/oz, silver/oz,
  BTC) with fetch timestamp should appear as a footnote below the table.

#### Allocation by Sector

All positions, on-platform and off-platform, grouped by sector. This is
NOT equities-only. Every position in the portfolio must appear in exactly
one sector row. Use the `sector` field from the portfolio JSON for IB
positions. Off-platform positions use the sectors assigned during
enrichment (Precious Metals, Cryptocurrency, Private Equity / Fintech,
Real Estate). Same dual-column format (% Liquid NAV, % Total NAV).

| Sector | Value (USD) | % Liquid NAV | % Total NAV |
|--------|-------------|--------------|-------------|
| Technology | | | |
| Energy | | | |
| Precious Metals | | | |
| Cryptocurrency | | | |
| Private Equity / Fintech | | | |
| Real Estate *(illiquid)* | | | |
| Cash & Cash Equivalents | | | |
| ... | | | |
| **Total** | | 100% | 100% |

Sectors are not predefined. Use the actual sectors present in the portfolio.
The table above is illustrative. Every sector with holdings must appear.

#### Allocation by Currency

All positions grouped by denomination currency. Off-platform assets:
precious metals and crypto are USD-denominated (global spot pricing),
private equity options are USD, real estate is in local currency (per
investor-context.md). Same dual-column format.

| Currency | Value (USD) | % Liquid NAV | % Total NAV |
|----------|-------------|--------------|-------------|

#### Allocation by Geography

All positions grouped by geographic exposure. Use the country/region of
the underlying business or asset, not the exchange listing. Off-platform:
precious metals = Global, crypto = Global, private equity = per company
domicile, real estate = per property location. Same dual-column format.

| Geography | Value (USD) | % Liquid NAV | % Total NAV |
|-----------|-------------|--------------|-------------|

#### Top 10 Positions

Top 10 positions by market value (with account label, including off-platform).

#### Concentration Flags

Computed on full portfolio including off-platform. Report as provided
in the portfolio JSON.

### Global Market Context
Summary of the global market research findings, structured by the
seven sections: macro data highlights, regime classification, credit
cycle, geopolitical risks, regional/sector developments, tactical
signals, and synthesis. This section is included in every analysis
regardless of mode. Keep it concise but comprehensive.

### Opportunity Landscape
Summary of the opportunity-scorer's findings (if available):
- Dominant regime and historical comparable periods (key parallels)
- Top 5 regime-fitted opportunities with conviction and time horizon
- Geopolitical tradeable expressions
- Regional divergence pair trades
If opportunity scoring was not available, note the omission.

### Impact Assessment
- Summary of thesis/market findings (mode-specific input combined
  with global context)
- Position-by-position impact matrix (table format):

| Position | Account | Exposure | Impact | Direction | Magnitude | Confidence |
|----------|---------|----------|--------|-----------|-----------|------------|

- New Opportunity Overlap Assessment table (if available):

| Opportunity | Overlaps With | Overlap Type | Assessment |
|-------------|---------------|--------------|------------|

### Key Takeaways
3-5 specific, actionable insights from the analysis. Each takeaway should
be one sentence stating a concrete finding and its portfolio implication.
Not generic statements ("markets are uncertain") but specific ones
("NVDA's 18.5% concentration creates asymmetric downside risk if AI
capex decelerates in H2 2026"). This section is the executive summary
of the analysis.

### Comparison Analysis (Mode 4 only)
- Source A summary
- Source B summary
- Agreement matrix
- Conflict matrix
- Positioning assessment: which scenario hurts more

### Risk Assessment
Structured by the five risk dimensions from the analysis framework.
Reference specific positions.

### Recommendations

Present each recommendation as a structured block with: source tag,
action, specific instrument (ticker, exchange), target account, position
size (conviction level, calculation, resulting %), rationale, proceeds
deployment (for TRIM/EXIT/REBALANCE), tax note, tradeoff, and priority.

Where Source is: `[IMPACT-DRIVEN]` or `[OPPORTUNITY-SCORER]`

For comparison mode, each recommendation also includes a Condition:
"Both scenarios", "If Source A", or "If Source B"

After all individual recommendation blocks, present a unified
**Action Plan** that combines the summary table with deployment
instructions for each recommendation in a single section:

#### Action Plan

**Action Summary Table:**

| # | Action | Ticker/Asset | Account | Size (% NAV) | Amount | Deployment | Source | Priority |
|---|--------|--------------|---------|--------------|--------|------------|--------|----------|

Where Deployment is one of:
- "Immediate" (for EXITs, TRIMs, and positions below 1% liquid NAV)
- "Staged: N weeks" (for ADDs/REBALANCEs above 1% liquid NAV)

For comparison mode, add a Condition column after Source.

Below the summary table, show total new capital deployed and post-trade
cash position.

**Deployment Schedule:**

For each recommendation with staged deployment (above 1% liquid NAV),
include its tranche table directly below the summary table, grouped
together. Format per recommendation:

**Rec N: [Ticker] ($[Amount])**

| Week | Action | Instrument | Tranche (%) | Amount | Entry Condition |
|------|--------|------------|-------------|--------|-----------------|

Abort conditions: [specific conditions for cancelling remaining tranches]

For immediate-execution recommendations, group them in a single line:
"Recommendations N, M, K: execute immediately at market open."

This unified section replaces the old separate Action Summary Table and
Staged Deployment Plan sections. Do NOT create separate sections for these.

### Steelman Check
For the top 3 recommendations, present the counter-case.

### Stress Test Results
For each stress scenario (minimum 2):
- Scenario name and description
- Trigger condition
- Estimated portfolio drawdown (% of liquid NAV)
- Position-level impact table:

| Position | Account | Weight (%) | Drawdown (%) | Loss Contribution (%) | Behaviour |
|----------|---------|------------|--------------|----------------------|-----------|

Where Behaviour is: hedge / neutral / amplifies

- Top 3 contributors to loss
- Top 3 positions providing protection
- Escalation flag triggered: yes/no

### Hedge Playbook

Concrete hedging strategies tied to each stress scenario, using live
options data and inverse ETF pricing from the IB gateway (when available).

#### Volatility Regime Context
- Current VIX level and classification (low/normal/elevated/high)
- What this means for hedge cost-effectiveness
- Source: `[LIVE]` (from hedge data) or `[ESTIMATED]` (WebSearch)

#### Per-Scenario Hedges

For each stress scenario (matching the Stress Test Results section):

**Scenario: [name]**

Hedge recommendation table:

| # | Instrument | Type | Strike/Level | Expiry | Delta | Contracts/Shares | Notional (USD) | Size (% Liq NAV) | Cost (USD) | Ann. Cost (%) | Activation | Drawdown Offset (%) |
|---|------------|------|-------------|--------|-------|------------------|----------------|-------------------|------------|---------------|------------|---------------------|

Where:
- Type: put option / inverse ETF / call option / collar / safe haven
- Activation: "carry as insurance" / "deploy on trigger: [condition]" / "scale in"
- Drawdown Offset: % of scenario's total portfolio drawdown this hedge offsets

Per-hedge rationale (2-3 sentences each):
- What specific portfolio exposure this hedge protects
- Why this instrument over alternatives
- What the hedge does NOT protect against (basis risk, limitations)

Data source label per hedge: `[LIVE]` or `[ESTIMATED]`

#### Hedge Portfolio Summary

**Overlap analysis:** Which hedges provide overlapping protection across
multiple scenarios. Group overlapping hedges.

**Consolidated hedge portfolio:**
- Total annual carry cost (USD and % of liquid NAV)
- Total notional protection
- Overlap-adjusted cost (removing redundant hedges)

**Cost-efficiency ranking:**

| Rank | Instrument | Ann. Cost (%) | Drawdown Offset (%) | Cost per 1% Protection | Scenarios Covered |
|------|------------|---------------|---------------------|----------------------|-------------------|

**Minimum viable hedge:** The single most cost-efficient hedge providing
the broadest protection. State instrument, cost, and coverage.

### Watchlist
Specific items to monitor with trigger conditions.

### Monitoring Framework

#### Monthly Macro Review
- Regime probability table variables to re-check
- Credit cycle transition signals
- Standing thesis validation points
- Threshold for triggering a full pipeline re-run

#### Weekly Position Review

| Position | Key Metric | Current Value | Reassessment Threshold |
|----------|-----------|---------------|------------------------|

#### Regime Shift Signals

| Signal | Current Value | Threshold | Recommended Action |
|--------|--------------|-----------|-------------------|

### Decision Triggers (Comparison mode only)
Specific signals that would confirm one source over the other.

### Previous Analysis Delta (if prior analysis exists)
If a previous portfolio-analysis-*.md file exists:
- What changed in the portfolio since last analysis
- Which previous recommendations were acted on
- Which previous watchlist items triggered
- Updated assessment of standing theses based on new data
Skip this section if no prior analysis file is found.

### Escalation Flags
List of threshold breaches and upstream re-run recommendations,
or "No escalation flags triggered." This section is consumed by
the orchestrator to decide whether to re-dispatch upstream subagents.

### Appendix: Full Position List
Complete position list across all accounts (IB + off-platform) with current
values. Off-platform positions included alongside IB positions. Sorted by
market value descending. Each row shows: ticker/asset name, account,
asset class, currency, quantity, price, market value (USD), % of liquid NAV,
unrealized P&L (0 for off-platform if cost basis unknown).
