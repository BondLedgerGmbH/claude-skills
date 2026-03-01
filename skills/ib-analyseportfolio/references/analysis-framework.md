<!-- analysis-framework.md
     Loaded by impact-analyst and recommendation-engine subagents.
     Provides the "how": behavioural constraints (voice, tone,
     anti-patterns) and the step-by-step analytical methodology.
     Steps 0-5 are executed by the impact-analyst subagent.
     Steps 6-9 are executed by the recommendation-engine subagent. -->

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

## Analysis Methodology

Note: In the subagent architecture, step 0 is handled by the
market-researcher subagent, steps 1-5 by the impact-analyst subagent,
and steps 6-9 by the recommendation-engine subagent. The steps below
define the complete methodology regardless of which subagent executes them.

### 0. Global Market Research (market-researcher subagent)
Execute the five-layer research methodology defined in the
market-researcher subagent. This runs before any mode-specific
analysis. The output provides the macro, geopolitical, regional,
sectoral, and tactical context that all subsequent analysis
is grounded in.

### 1. Portfolio Snapshot
- Combined NAV across both accounts
- Allocation by: asset class, sector, geography, currency denomination
- Per-account breakdown (for tax-aware recommendations)
- Concentration flags: as computed by MCP server using configured thresholds
  (included in portfolio-summary-{timestamp}.json)

### 2. Correlation and Cluster Analysis
- Identify groups of holdings likely to move together in drawdowns
- Flag indirect exposures (e.g., ETFs with heavy NVDA weighting,
  cloud providers dependent on AI capex)
- Assess USD concentration across all holdings
  (including USD-denominated equities, ETFs, stablecoins)

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
- Total USD exposure (direct + indirect)
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
- Action: [TRIM], [EXIT], [ADD], [REBALANCE], [HEDGE]
- Strategic intent: [RISK MITIGATION], [GROWTH OPTIMIZATION], [USD HEDGE]
- Target account: specify which account (corporate or personal, or both)
- Rationale: why this action, referencing the thesis/event
- Proceeds deployment (required for TRIM, EXIT, REBALANCE): where the
  freed capital goes. Must be specific: name the target instrument(s),
  asset class, or cash reserve. If proceeds should be split across
  multiple targets, state the split. If proceeds should remain as cash,
  state why (e.g., "hold as USD cash in corporate account to preserve
  buying power for opportunistic entry on X"). Never leave proceeds unaddressed.
- Tax note: reference the tax treatment defined in investor-context.md
  for the target account. Flag dividend withholding where relevant.
- Tradeoff: what you give up by taking this action
- Priority: High / Medium / Low

### 7. Steelman Check
For every major recommendation:
- What is the strongest case against this recommendation?
- Under what conditions would this be the wrong move?
- What signal would invalidate the thesis behind it?

### 8. Watchlist
Flag positions or macro indicators to monitor over next 6-12 months:
- Earnings dates or catalysts for held positions
- Policy developments (Fed, ECB, SNB, fiscal)
- Signals that would cause revision of standing theses

### 9. Comparison Analysis (Mode 4 only)
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
