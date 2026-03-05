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
- Combined portfolio NAV
- Number of positions across both accounts

### Portfolio Snapshot
- Combined allocation table (asset class, sector, currency, geography)
- Top 10 positions by market value (with account label)
- Concentration flags

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
Complete position list across both accounts with current values.
Sorted by market value descending.
