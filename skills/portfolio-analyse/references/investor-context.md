<!-- investor-context.md
     Loaded by all three subagents: market-researcher (for standing
     theses), impact-analyst, and recommendation-engine.
     Provides the "who" and "why": investor profile, account structure,
     tax rules, and standing investment theses.
     The user maintains this file. Skill warns if stale (90+ days).

     NOTE: This is a TEMPLATE with example data. Replace all values
     with your actual investor profile, holdings, and theses. -->

# Investor Context

## Profile
- Age: 35
- Location: Example City, Switzerland
- Investment horizon: 3-5 years (default; can be adjusted per analysis)
- Household: Single / Married couple
- Risk profile: Aggressive growth, high volatility tolerance
- Geographic scope: Open to international exposure and non-USD assets

## Account Structure

### Corporate Account
- Type: Example Canton domiciled GmbH
- Tax treatment: Corporate income tax on realized gains
- Dividend withholding: Subject to withholding tax; reclaim considerations
  under applicable treaties (e.g., US-CH treaty: 15% rate)
- Participation exemption: May apply to qualifying equity holdings
  (verify current cantonal rules)

### Personal Account (Individual)
- Type: Private investor
- Tax treatment: No capital gains tax on private investments
  (standard Swiss treatment for stocks, crypto, real estate)
- Dividend income: Taxed as income
- Crypto: Verify current cantonal treatment of digital assets

### Off-Platform Holdings (Not in IB)
These assets are held outside Interactive Brokers. The orchestrator merges
them into the portfolio-summary JSON at runtime (Step 2.5) with current
spot prices. Subagents see them as positions with `account: "off_platform"`
and `source: "manual"`. Update quantities here when holdings change.

**Precious Metals (physical, stored privately):**
- Gold: 2 oz
- Silver: 100 oz
- Valuation: Use current spot prices at time of analysis

**Cryptocurrency:**
- Bitcoin: 0.5 BTC
- Valuation: Use current spot price at time of analysis

**Private Equity / Stock Options:**
- Example Corp: 1,000 stock options at FMV $50/share
  ($50,000 notional value)
- Liquid: Treat as liquid if secondary market exists, illiquid otherwise.
- Note: Exercise terms, vesting schedule, and strike price not
  specified. Use FMV for wealth calculations.

**Real Estate:**
- Primary residence: $500,000
- Investment property: $200,000
- Total real estate: $700,000
- Note: Illiquid. Include in total wealth and asset allocation
  calculations. Do not include in liquid net worth.

**Note:** These holdings are injected into the portfolio-summary JSON by the
orchestrator. The JSON `combined.liquid_nav` includes all liquid off-platform
assets. The `combined.total_wealth` includes illiquid real estate.
Subagents do not need to calculate these values manually.

## Cash Policy

- **Target uninvested cash:** 0% of liquid NAV
- **Rationale:** All idle cash must be deployed into money market funds
  or short-duration fixed income. SGOV (USD), XEON (EUR), CSH2 (EUR)
  are the preferred vehicles — T+0/T+1 liquid, near-zero credit risk,
  yield-generating. Holding uninvested cash is never acceptable when
  these instruments are available.
- **Currency split for cash deployment:** Follow any active currency
  thesis. Prefer EUR-denominated money market (XEON/CSH2) over
  USD (SGOV) for new cash deployment unless there is a specific
  near-term need for USD liquidity.
- **Exception:** Small operational cash buffer (<$500 per account) is
  acceptable to cover fees, FX settlement, and order execution slippage.

## Standing Theses

These theses should be factored into every analysis unless
explicitly overridden by the user.

**Staleness check:** The skill should check the last-modified date of
this file on every run. If investor-context.md has not been modified
in 90+ days, include a note in the chat summary reminding the user
to review and update their standing theses. Theses evolve, and stale
theses lead to stale recommendations.

### Example Thesis 1: AI Bubble
- AI/semiconductor valuations are stretched
- Not confident in NVIDIA's short-term growth despite long-term tailwinds
- Want to reduce concentration risk without fully exiting AI exposure
- Monitor: "picks and shovels" plays, infrastructure beneficiaries
  with less valuation stretch

### Example Thesis 2: USD Deterioration
- US debt trajectory is unsustainable
- Long-term USD devaluation expected
- Potential loss of confidence in US Treasuries as "risk-free" asset
- Want to hedge/reduce USD exposure while maintaining access to
  US growth assets where appropriate

### Example Thesis 3: Defence & Robotics
- Autonomous drones fundamentally change warfare economics
- Pentagon and NATO ramping drone procurement
- Monitor: contract awards, regulatory changes, civilian spillover

### Example Thesis 4: Private Credit Stress
- Private credit AUM has grown rapidly with limited oversight
- Default rates rising, PIK usage increasing
- Monitor: default indices, BDC discount-to-NAV trends

## Analyst Expectations
- Institutional-grade analysis (think UHNW family office level)
- Creative and contrarian ideas, not generic advisory output
- Explicit tradeoff discussion for every recommendation
- No "consult a financial advisor" disclaimers
- Conservative capital-preservation ideas are acceptable when there is
  a clear signal markets are in trouble and flight to safety is the
  most logical action under current circumstances. Do not default to
  conservative bias otherwise.
- Specific tickers and positions referenced, not generic asset classes
- Steelman opposing views to avoid confirmation bias
