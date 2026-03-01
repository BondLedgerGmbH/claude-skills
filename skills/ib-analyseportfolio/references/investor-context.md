<!-- investor-context.md
     Loaded by all three subagents: market-researcher (for standing
     theses), impact-analyst, and recommendation-engine.
     Provides the "who" and "why": investor profile, account structure,
     tax rules, and standing investment theses.
     The user maintains this file. Skill warns if stale (90+ days). -->

<!-- ============================================================
     IMPORTANT: Replace all [PLACEHOLDER] values with your actual
     data before running the skill. The skill will not produce
     accurate results with placeholder values.
     ============================================================ -->

# Investor Context

## Profile
- Age: [YOUR_AGE]
- Location: [YOUR_CITY, YOUR_COUNTRY]
- Investment horizon: [e.g., 3-5 years]
- Household: [e.g., Single / Married couple / Family]
- Risk profile: [e.g., Aggressive growth / Balanced / Conservative]
- Geographic scope: [e.g., Open to international exposure and non-USD assets]

## Account Structure

<!-- Define each IB account below. Add or remove account sections
     as needed. The skill supports multiple accounts with different
     tax treatments. -->

### [ACCOUNT_1_NAME] (Corporate Account)
- Type: [e.g., Domiciled GmbH / Delaware LLC / Ltd]
- Tax treatment: [e.g., Corporate income tax on realized gains]
- Dividend withholding: [e.g., Subject to withholding tax; reclaim under applicable treaties]
- Participation exemption: [e.g., May apply to qualifying equity holdings]

### [ACCOUNT_2_NAME] (Individual Account)
- Type: [e.g., Private investor]
- Tax treatment: [e.g., No capital gains tax / Long-term capital gains rate]
- Dividend income: [e.g., Taxed as income]
- Crypto: [e.g., Verify current treatment of digital assets in your jurisdiction]

### Off-Platform Holdings (Not in IB)
These assets are held outside Interactive Brokers and are not visible
in portfolio data pulls. Subagents must factor them into total wealth
calculations, concentration analysis, and recommendations.

<!-- List any assets held outside IB. Remove sections that don't
     apply. Use current market values. -->

**Precious Metals (physical):**
- Gold: [AMOUNT] oz
- Silver: [AMOUNT] oz
- Valuation: Use current spot prices at time of analysis

**Cryptocurrency:**
- Bitcoin: [AMOUNT] BTC
- [OTHER_CRYPTO]: [AMOUNT]
- Valuation: Use current spot price at time of analysis

**Private Equity / Stock Options:**
- [COMPANY_NAME]: [NUMBER] stock options at FMV $[PRICE]/share
  ($[NOTIONAL_VALUE] notional value)
- Liquid: [Yes/No - describe liquidity]
- Note: [Exercise terms, vesting schedule, strike price details]

**Real Estate:**
- Primary residence: $[VALUE]
- Investment property: $[VALUE]
- Total real estate: $[TOTAL_VALUE]
- Note: Illiquid. Include in total wealth and asset allocation
  calculations. Do not include in liquid net worth.

**Subagent instructions:** When calculating total wealth, sum IB NAV +
off-platform holdings at current valuations. When assessing
concentration, allocation, or recommending new positions, account for
these holdings to avoid double-exposures (e.g., do not recommend
adding gold if precious metals allocation is already substantial).
Distinguish between liquid wealth (IB + precious metals + crypto)
and total wealth (liquid + options + real estate) where relevant.

## Standing Theses

These theses should be factored into every analysis unless
explicitly overridden by the user.

**Staleness check:** The skill should check the last-modified date of
this file on every run. If investor-context.md has not been modified
in 90+ days, include a note in the chat summary reminding the user
to review and update their standing theses. Theses evolve, and stale
theses lead to stale recommendations.

<!-- Define your standing investment theses below. These are your
     core convictions that should inform every analysis. Add, remove,
     or modify theses as your views evolve. -->

### [THESIS_1_NAME]
- [Core belief or conviction]
- [Supporting rationale]
- [What you want to do about it: reduce exposure, hedge, etc.]
- Monitor: [Signals or indicators to watch]

### [THESIS_2_NAME]
- [Core belief or conviction]
- [Supporting rationale]
- [What you want to do about it]
- Monitor: [Signals or indicators to watch]

### [THESIS_3_NAME]
- [Core belief or conviction]
- [Supporting rationale]
- [What you want to do about it]
- Monitor: [Signals or indicators to watch]

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
