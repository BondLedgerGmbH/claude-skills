<!-- output-template.md
     Loaded by recommendation-engine subagent.
     Provides the "what": the required sections and structure for
     the final analysis MD. Every section listed here must appear
     in the output unless marked as conditional.
     The recommendation-engine incorporates content from earlier
     subagent outputs (market research, opportunity scoring, impact
     analysis) into this template structure. -->

# Output Template

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
|   Stock options | | | |
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

Present as a structured list, then summarize in the Action Summary Table:

| # | Action | Ticker/Asset | Account | Size (% NAV) | Source | Strategic Intent | Tax Note | Priority |
|---|--------|--------------|---------|--------------|--------|------------------|----------|----------|

Where Source is: `[IMPACT-DRIVEN]` or `[OPPORTUNITY-SCORER]`

For comparison mode, add a Condition column:

| # | Action | Ticker/Asset | Account | Size (% NAV) | Source | Condition | Strategic Intent | Tax Note | Priority |
|---|--------|--------------|---------|--------------|--------|-----------|------------------|----------|----------|

Where Condition is one of: "Both scenarios", "If Source A", "If Source B"

Each recommendation must include: source tag, action, specific instrument
(ticker, exchange), target account, position size (conviction level,
calculation, resulting %), rationale, proceeds deployment (for
TRIM/EXIT/REBALANCE), tax note, tradeoff, and priority.

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

### Staged Deployment Plan
For each ADD/REBALANCE recommendation above 1% liquid NAV:
- Instrument and total target allocation
- Tranche table:

| Week | Action | Instrument | Tranche (%) | Amount | Entry Condition |
|------|--------|------------|-------------|--------|-----------------|

- Abort conditions
For smaller positions: note immediate full entry.

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
