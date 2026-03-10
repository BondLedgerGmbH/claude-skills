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
  (SPY, QQQ) do NOT need footnotes. Account names (BondLedger,
  Personal) do not need footnotes. Standard units (USD, EUR, CHF, oz,
  BTC) do not need footnotes.
- Thesis-derived bracket labels (e.g. `[INTEL]`, `[USD_DET]`,
  `[AI_BUBBLE]`) must be footnoted with the full thesis name from
  investor-context.md on first use.

## Document Structure Overview

The report is front-loaded for action. The main body contains only what
the reader needs to make decisions: snapshot, macro summary, key
takeaways, recommendations (with merged summary table), and hedging.
All supporting analysis, monitoring, and reference material lives in
the Appendix. The reader can drill into the Appendix for evidence
behind any recommendation.

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
|   Stock options (e.g. Payward) | | | |
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

### Global Market Context

#### Executive Summary
2-3 paragraph narrative summarising the current macro environment in plain
language. Cover: what regime we are in and why, the dominant risks and
tailwinds, and the single most important thing an investor should know
right now. This is the "if you read nothing else" section. No tables,
no jargon, no bracket labels. Written for a smart non-specialist.

The Detailed Findings (macro data, regime classification, credit cycle,
geopolitical risks, regional/sector developments, tactical signals,
synthesis) are in the Appendix.

### Key Takeaways
3-5 specific, actionable insights from the analysis. Each takeaway should
be one sentence stating a concrete finding and its portfolio implication.
Not generic statements ("markets are uncertain") but specific ones
("NVDA's 18.5% concentration creates asymmetric downside risk if AI
capex decelerates in H2 2026"). This section is the executive summary
of the analysis.

### Recommendations

This is the single most important section of the report. It starts with
a high-level summary table, then provides detailed recommendation blocks,
coverage checks, and cash logistics.

#### Summary

A merged action-and-deployment table. Every recommendation appears here.
If a recommendation is deployed across multiple tranches, it occupies
multiple rows (one per tranche). Immediate-execution recommendations
occupy a single row.

| # | Action | Ticker/Asset | Account | From | To | Amount (USD) | Size (% Liq NAV) | Execute | Entry Condition | Source | Priority |
|---|--------|--------------|---------|------|----|-------------|------------------|---------|-----------------|--------|----------|

Column definitions:
- **#:** Recommendation number. Repeated across tranche rows for the
  same recommendation.
- **From (Fund Source):** Where the capital comes from. For ADDs: "Cash",
  "USD cash", "EUR cash", or "Proceeds from Rec N". For TRIMs/EXITs:
  the position being sold. For REBALANCEs: the source position.
- **To (Target Instrument):** The specific instrument being bought.
  For TRIMs/EXITs: "Cash" or "Deploy per Rec N" if proceeds are earmarked.
- **Amount (USD):** Dollar amount of the trade (tranche amount for staged
  deployments, full amount for immediate).
- **Size (% Liq NAV):** Position size as percentage of liquid NAV (tranche
  size for staged deployments, full size for immediate).
- **Execute:** Absolute calendar week using ISO format: "CW{nn}" (e.g.
  "CW11", "CW12"). For immediate-execution trades, use the current
  calendar week. For staged tranches, use the specific calendar week
  for each tranche. Never use relative labels like "Week 1", "Week 2".
- **Entry Condition:** For immediate trades: "Market open". For staged
  tranches: price level, macro confirmation signal, technical support
  level, or "Time-based (deploy regardless)".

**Sorting and numbering:** The summary table and the Recommendation
Details section below are both sorted by execution urgency: earliest
Execute week first, then by priority (High > Medium > Low) within the
same week. **Recommendation numbers (#) must be assigned sequentially
in this sorted order** — Rec 1 is the most urgent, Rec 2 is next, etc.
Do NOT assign numbers by source type or any other grouping and then
re-sort; the numbering itself must reflect urgency order.
- **Source:** `[IMPACT-DRIVEN]` or `[OPPORTUNITY-SCORER]`
- **Priority:** High / Medium / Low

For comparison mode, add a Condition column after Source.

Below the table, show:
- Total new capital deployed (USD)
- Total capital freed (USD)
- Net cash flow
- Post-trade cash position (USD and % of liquid NAV)

For each staged recommendation, show abort conditions below the table:
- **Rec N abort:** [specific conditions for cancelling remaining tranches]

For immediate-execution recommendations, group them:
"Recommendations N, M, K: execute immediately at market open."

This unified table replaces the old separate Action Summary Table,
Deployment Schedule, and Action Plan sections. Do NOT create separate
sections for these.

**Inter-Account Cash Rebalance:**

Determine whether each account has enough cash to fund its recommendations.
Compare available cash per account against capital required per account.

| Account | Available Cash (USD) | Capital Required (USD) | Surplus / Shortfall (USD) |
|---------|---------------------|----------------------|--------------------------|

If any account has a shortfall:

| Transfer | From Account | To Account | Amount (USD) | Method | Timing |
|----------|-------------|------------|-------------|--------|--------|

Where:
- Method: "Internal transfer" (between IB accounts), "Wire transfer"
  (off-platform to IB), or "IB withdrawal + deposit" (between IB
  accounts at different brokers if applicable)
- Timing: "Before Week 1 trades" or "Before Week N trades" (aligned
  with the deployment schedule)

Notes:
- Account for proceeds from TRIM/EXIT recommendations that free cash
  within the same account (these reduce the shortfall).
- If recommendations span multiple currencies, note any FX conversion
  needed and which account should hold the converted currency.
- If all accounts have sufficient cash: state "No inter-account
  transfers required."

#### Recommendation Details

Present each recommendation as a structured block sorted by execution
urgency (earliest Execute week first, then by priority within the same
week). Each block includes: execution timing (calendar week and urgency
context, e.g. "**Execute: CW11 (Immediate)** — execute at next market
open" or "**Execute: CW13** — deploy after confirming oil stays above
$95"), source tag, action, specific instrument (ticker, exchange),
target account, position size (conviction level, calculation, resulting
%), rationale, proceeds deployment (for TRIM/EXIT/REBALANCE), tax note,
tradeoff, and priority.

Where Source is: `[IMPACT-DRIVEN]` or `[OPPORTUNITY-SCORER]`

For comparison mode, each recommendation also includes a Condition:
"Both scenarios", "If Source A", or "If Source B"

#### Regime Opportunity Coverage

Every opportunity from the Opportunity Landscape must be explicitly
addressed here. This ensures no regime-fitted opportunity is silently
ignored.

**Actioned opportunities:** For each opportunity that resulted in a
recommendation above, reference the recommendation number:

| Opportunity | Rec # | Action | Instrument | Rationale |
|-------------|-------|--------|------------|-----------|

**Not actioned opportunities:** For each opportunity that was NOT
recommended, explain why. Valid reasons include: already sufficiently
exposed, overlap with existing holdings, insufficient conviction,
capital constraints, tax inefficiency, or timing. Be specific.

| Opportunity | Existing Exposure | Reason Not Actioned |
|-------------|-------------------|---------------------|

#### Regime Loser Exposure Check

Every loser from the Top 5 Losers table must be cross-referenced against
the current portfolio. This ensures losers held in the portfolio are
either actioned or explicitly justified.

**Held losers requiring action:** If the portfolio holds a position in
a flagged loser sector/asset, and a recommendation above addresses it,
reference the recommendation:

| Loser | Portfolio Position(s) | Exposure (% Liq NAV) | Rec # | Action |
|-------|-----------------------|----------------------|-------|--------|

**Held losers — no action needed:** If the portfolio holds exposure to a
flagged loser but no action is warranted, explain why. Valid reasons
include: position is small enough to be immaterial, the position serves
a different strategic purpose (e.g. dividend income, hedge), the loser
flag is sector-wide but this specific name is an exception, or the
position has tax reasons to hold.

| Loser | Portfolio Position(s) | Exposure (% Liq NAV) | Reason No Action |
|-------|-----------------------|----------------------|------------------|

**No exposure:** List any losers where the portfolio has zero exposure
(confirmation that we are not exposed).

#### New Opportunity Overlap Assessment (if available)

Show which new opportunities from the Opportunity Landscape overlap with
existing holdings. This contextualises the [OPPORTUNITY-SCORER]
recommendations and informs the summary table above.

| Opportunity | Overlaps With | Overlap Type | Assessment |
|-------------|---------------|--------------|------------|

Where Assessment is: `PROCEED` (no meaningful overlap), `CAUTION`
(partial overlap, justify adding), or `REDUNDANT` (skip).

### Stress Testing & Hedging

Stress scenarios with integrated hedge strategies. Each scenario shows
the portfolio impact AND the specific hedges to protect against it.
Hedges must account for the recommended portfolio (current holdings +
all recommendations applied), not just existing positions. This ensures
hedges complement the growth recommendations above rather than
conflicting with them.

#### Hedge Summary

A consolidated table of ALL hedge instruments across all scenarios.
This table appears first, before individual scenario detail, serving
the same purpose as the Summary table does for Recommendations: a
quick-reference view of every hedge action.

| # | Scenario | Instrument | Type | Strike/Level | Expiry | Delta | Contracts/Shares | Notional (USD) | Size (% Liq NAV) | Cost (USD) | Ann. Cost (%) | Activation | Drawdown Offset (%) | Data Source |
|---|----------|------------|------|-------------|--------|-------|------------------|----------------|-------------------|------------|---------------|------------|---------------------|-------------|

Where:
- **#:** Hedge number (H1, H2, ...). Referenced in scenario details below.
- **Scenario:** Which scenario this hedge primarily targets. If it covers
  multiple scenarios, list all (e.g. "S1, S2").
- **Type:** put option / inverse ETF / call option / collar / safe haven
- **Activation:** "carry as insurance" / "deploy on trigger: [condition]" / "scale in"
- **Data Source:** `[LIVE]` or `[ESTIMATED]`

Below the table, show:
- Total annual carry cost (USD and % of liquid NAV)
- Overlap-adjusted cost (removing redundant hedges that cover the same exposure)
- **Minimum viable hedge:** The single most cost-efficient hedge providing
  the broadest protection. State instrument, cost, and coverage.

#### Volatility Regime Context
- Current VIX level and classification (low/normal/elevated/high)
- What this means for hedge cost-effectiveness
- Source: `[LIVE]` (from hedge data) or `[ESTIMATED]` (WebSearch)

#### Scenarios

For each stress scenario (minimum 2):

**Scenario N: [name]**

*Impact:*
- Description (2-3 sentences)
- Trigger condition
- Estimated portfolio drawdown (% of liquid NAV)
- Position-level impact table:

| Position | Account | Weight (%) | Drawdown (%) | Loss Contribution (%) | Behaviour |
|----------|---------|------------|--------------|----------------------|-----------|

Where Behaviour is: hedge / neutral / amplifies

- Top 3 contributors to loss
- Top 3 positions providing protection
- Escalation flag triggered: yes/no

*Hedge Strategy:*

Reference hedges from the Hedge Summary table by number (H1, H2, etc.)
and provide per-hedge rationale (2-3 sentences each):
- What specific portfolio exposure this hedge protects
- Why this instrument over alternatives (consider whether recommended
  positions already provide natural hedging for this scenario)
- What the hedge does NOT protect against (basis risk, limitations)

If a hedge instrument also provides protection for other scenarios,
note this inline: "Also covers Scenario N: [brief explanation]."

#### Hedge Cost-Efficiency

**Cost-efficiency ranking:**

| Rank | Instrument | Ann. Cost (%) | Drawdown Offset (%) | Cost per 1% Protection | Scenarios Covered |
|------|------------|---------------|---------------------|----------------------|-------------------|

### Comparison Analysis (Mode 4 only)
- Source A summary
- Source B summary
- Agreement matrix
- Conflict matrix
- Positioning assessment: which scenario hurts more

### Decision Triggers (Comparison mode only)
Specific signals that would confirm one source over the other.

### Appendix

#### Global Market Context: Detailed Findings
Summary of the global market research findings, structured by the
seven sections: macro data highlights, regime classification, credit
cycle, geopolitical risks, regional/sector developments, tactical
signals, and synthesis. This section is included in every analysis
regardless of mode. Keep it concise but comprehensive.

#### Opportunity Landscape
Summary of the opportunity-scorer's findings (if available):
- Dominant regime and historical comparable periods (key parallels)
- Top 5 regime-fitted opportunities with conviction and time horizon
- Top 5 regime-fitted losers (assets/sectors most likely to underperform
  in the current regime, with conviction and rationale). These are
  "what NOT to buy" signals. Same table format as opportunities but
  showing the worst-positioned assets given current conditions.
- Geopolitical tradeable expressions
- Regional divergence pair trades
If opportunity scoring was not available, note the omission.

#### Impact & Risk Assessment
Combined assessment of how current conditions affect the portfolio.

**Thesis / Market Impact Summary:**
Summary of thesis/market findings (mode-specific input combined with
global context). What is happening and why it matters for this portfolio.

**Position Impact Matrix:**

| Position | Account | Exposure | Impact | Direction | Magnitude | Confidence |
|----------|---------|----------|--------|-----------|-----------|------------|

**Risk Dimensions:**
Structured by the five risk dimensions from the analysis framework.
Reference specific positions. For each dimension, state the current
risk level and which positions are most exposed.

#### Steelman Check
For the top 3 recommendations, present the counter-case.

#### Watchlist
Specific items to monitor with trigger conditions.

#### Monitoring Framework

**Monthly Macro Review:**
- Regime probability table variables to re-check
- Credit cycle transition signals
- Standing thesis validation points
- Threshold for triggering a full pipeline re-run

**Weekly Position Review:**

| Position | Key Metric | Current Value | Reassessment Threshold |
|----------|-----------|---------------|------------------------|

**Regime Shift Signals:**

| Signal | Current Value | Threshold | Recommended Action |
|--------|--------------|-----------|-------------------|

#### Previous Analysis Delta (if prior analysis exists)
If a previous portfolio-analysis-*.md file exists:
- What changed in the portfolio since last analysis
- Which previous recommendations were acted on
- Which previous watchlist items triggered
- Updated assessment of standing theses based on new data
Skip this section if no prior analysis file is found.

#### Escalation Flags
List of threshold breaches and upstream re-run recommendations,
or "No escalation flags triggered." This section is consumed by
the orchestrator to decide whether to re-dispatch upstream subagents.

#### Allocation by Sector

| Sector | Value (USD) | % Liquid NAV | % Total NAV |
|--------|-------------|--------------|-------------|

Include all on-platform and off-platform positions. Classify off-platform
holdings into appropriate sectors (Precious Metals, Cryptocurrency,
Private Equity / Fintech, Real Estate).

#### Allocation by Currency

| Currency | Value (USD) | % Liquid NAV | % Total NAV |
|----------|-------------|--------------|-------------|

#### Allocation by Geography

| Region | Value (USD) | % Liquid NAV | % Total NAV |
|--------|-------------|--------------|-------------|

Use issuer domicile, not listing exchange. Off-platform holdings:
precious metals → Global, crypto → Global, real estate → by property
location, private equity → by company domicile.

#### Top 10 Positions

| # | Position | Account | Value (USD) | % Liquid NAV |
|---|----------|---------|-------------|--------------|

Across all accounts (IB + off-platform). Sorted by market value descending.

#### Concentration Flags

List any position or sector exceeding 10% of liquid NAV. For each flag:
- Position/sector name, account, current weight
- Whether this is intentional (thesis-driven) or drift
- Risk note

If no flags: "No concentration flags triggered."

#### Full Position List
Complete position list across all accounts (IB + off-platform) with current
values. Off-platform positions included alongside IB positions. Sorted by
market value descending. Each row shows: ticker/asset name, account,
asset class, currency, quantity, price, market value (USD), % of liquid NAV,
unrealized P&L (0 for off-platform if cost basis unknown).
