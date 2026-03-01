<!-- output-template.md
     Loaded by recommendation-engine subagent.
     Provides the "what": the required sections and structure for
     the final analysis MD. Every section listed here must appear
     in the output unless marked as conditional.
     The recommendation-engine incorporates content from earlier
     subagent outputs (market research, impact analysis) into this
     template structure. -->

# Output Template

## Required Sections

### Header
- Analysis date and time
- Mode: Thesis / YouTube Transcript / Market Scan / Comparison
- If thesis mode: one-line summary of the input thesis
- If YouTube mode: video title, channel, URL, and one-line summary of content
- If comparison mode: one-line summary of each source
- Global market research: fresh or cached (if cached, show age, e.g., "cached from 3 hours ago")
- Combined portfolio NAV
- Number of positions across both accounts

### Portfolio Snapshot
- Combined allocation table (asset class, sector, currency, geography)
- Top 10 positions by market value (with account label)
- Concentration flags

### Global Market Context
Summary of the global market research findings, structured by the
five layers. This section is included in every analysis regardless
of mode. Keep it concise but comprehensive - the key developments
that form the backdrop for the analysis.

### Impact Assessment
- Summary of thesis/market findings (mode-specific input combined
  with global context)
- Position-by-position impact matrix (table format):

| Position | Account | Exposure | Impact | Direction | Magnitude | Confidence |
|----------|---------|----------|--------|-----------|-----------|------------|

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

| # | Action | Ticker/Asset | Account | Strategic Intent | Tax Note | Priority |
|---|--------|--------------|---------|------------------|----------|----------|

For comparison mode, add a Condition column:

| # | Action | Ticker/Asset | Account | Condition | Strategic Intent | Tax Note | Priority |
|---|--------|--------------|---------|-----------|------------------|----------|----------|

Where Condition is one of: "Both scenarios", "If Source A", "If Source B"

### Steelman Check
For the top 3 recommendations, present the counter-case.

### Decision Triggers (Comparison mode only)
Specific signals that would confirm one source over the other.

### Watchlist
Specific items to monitor with trigger conditions.

### Previous Analysis Delta (if prior analysis exists)
If a previous portfolio-analysis-*.md file exists in OUTPUT_DIR:
- What changed in the portfolio since last analysis
- Which previous recommendations were acted on
- Which previous watchlist items triggered
- Updated assessment of standing theses based on new data
Skip this section if no prior analysis file is found.

### Appendix: Full Position List
Complete position list across both accounts with current values.
Sorted by market value descending.
