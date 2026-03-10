---
name: portfolio-analyse
description: >
  Analyse an investment portfolio held across Interactive Brokers accounts and
  off-platform holdings (physical precious metals, cryptocurrency, private
  equity options, real estate) against a specific thesis, research, or market
  conditions. Off-platform assets are treated as first-class positions alongside
  IB holdings in all analysis stages. Operates in four modes: (1) Thesis mode -
  user provides an MD file with research, macro thesis, or transcript analysis;
  (2) YouTube mode - user provides a YouTube URL, the skill extracts the
  transcript via the yt-transcript skill (supports auto-translated and
  non-English videos) and analyses the portfolio against the video content;
  (3) Market scan mode - no input provided, the skill performs a broad web
  search for current macro/market developments and analyses the portfolio
  against those findings; (4) Comparison mode - user provides two inputs
  (any combination of MD files and/or YouTube URLs), the skill analyses both
  perspectives against the portfolio and highlights where they agree, conflict,
  and what that means for positioning. Use this skill when the user wants to:
  assess how news/research/events/videos impact their portfolio, get
  portfolio-wide risk analysis, check concentration or currency exposure, get
  tax-aware recommendations across IB and off-platform accounts, run a broad
  market scan, or compare two opposing views against their holdings. Also
  trigger when the user mentions "portfolio analysis", "position review",
  "market impact on my holdings", "what should I do with my portfolio", "analyse
  this video against my portfolio", "compare these two views", or references
  their IB accounts or off-platform holdings in an investment context.
---

# Portfolio Analysis Engine

## Configuration

```
RESEARCH_CACHE_TTL_HOURS = 6
PORTFOLIO_CACHE_TTL_MINUTES = 60
INTERMEDIATE_FILE_MAX_AGE_DAYS = 7
RESEARCH_CACHE_MAX_AGE_HOURS = 24
MAX_ESCALATION_RETRIES = 1
DATA_QUALITY_UNAVAILABLE_THRESHOLD_PCT = 20
PROJECT_DIR = <your-project-directory>
OUTPUT_DIR = <your-project-directory>/output/ib-analysis
SKILL_DIR = <your-project-directory>/.claude/skills/portfolio-analyse
AGENTS_DIR = <your-project-directory>/.claude/agents
```

## Output Directory Structure

All intermediate and final files are organised in per-stage subdirectories:

```
OUTPUT_DIR/
├── 0-portfolio-snapshots/     ← portfolio-summary-{timestamp}.json
├── 0-thesis-inputs/           ← thesis-input-{timestamp}.md
├── 1-market-research/         ← market-research-cache-{timestamp}.md
├── 2-opportunity-scoring/     ← opportunity-scoring-{timestamp}.md
├── 3-impact-analysis/         ← impact-analysis-{timestamp}.md
├── 3-hedge-data/              ← hedge-data-{timestamp}.json
└── 4-portfolio-analysis/      ← portfolio-analysis-{timestamp}.md (final output)
```

## Dependencies

- MCP server `ib-connect` must be configured and available (provides `ib_status`, `ib_start_gateway`, `ib_portfolio_summary`, `ib_option_chain`, `ib_market_snapshot` tools)
- `yt-transcript` skill must be installed for YouTube mode and comparison mode with YouTube URLs
- Four custom subagents in `.claude/agents/`: `market-researcher.md`, `opportunity-scorer.md`, `impact-analyst.md`, `recommendation-engine.md`

## Execution Flow

### Step 1: Ensure output directory exists

Create `OUTPUT_DIR` and all subdirectories if they do not exist:
`0-portfolio-snapshots/`, `0-thesis-inputs/`, `1-market-research/`,
`2-opportunity-scoring/`, `3-impact-analysis/`, `3-hedge-data/`,
`4-portfolio-analysis/`.

### Step 2: Pull portfolio data

**Check for cached portfolio snapshot first.** Look for existing `portfolio-summary-*.json` files in `OUTPUT_DIR/0-portfolio-snapshots/`. Find the most recent one by filename timestamp. If it exists and is within `PORTFOLIO_CACHE_TTL_MINUTES` (default 60 minutes): reuse it. Set the portfolio file path to the cached file. Log: "Using cached portfolio snapshot from {age} minutes ago." Skip directly to validation below.

This cache is critical for concurrent execution: multiple analysis runs (e.g., 4 terminal tabs with different thesis inputs) share the same portfolio snapshot without overwriting each other. The MCP server also has its own 60-minute cache, so even a fresh pull is fast if the MCP cache is warm.

**If no valid cached snapshot exists:**

Call `ib_status(account="all")` to check connectivity.

- If `gateway_not_running` for any account: call `ib_start_gateway(account="all")`. Tell the user gateways are starting and they need to complete browser authentication. Wait for user confirmation that authentication is done, then re-check status.
- If `auth_required` for any account: call `ib_reauthenticate(account="all")`. Tell the user which accounts need login. Wait for user confirmation, then re-check status.
- If all accounts authenticated: proceed.

Call `ib_portfolio_summary(account="all")`. Do NOT use `force_refresh=true` unless the user explicitly requests fresh data. The MCP server returns cached data if within its own TTL, which is fast and avoids redundant IB API calls.

- If error response: report the error and stop.
- If success: save the full response as `OUTPUT_DIR/0-portfolio-snapshots/portfolio-summary-{YYYY-MM-DD-HH-MM-SS}.json` with `chmod 600`. This timestamped file is the canonical portfolio handoff to all subagents for this run.

**Validate portfolio data** (applies to both cached and fresh snapshots):
- At least one account must have non-zero NAV. If all zero: stop and report.
- Positions key must be present (can be empty array for cash-only portfolios). If missing: stop and report malformed data.

### Step 2.5: Enrich portfolio with off-platform holdings

After obtaining the IB portfolio snapshot (fresh or cached), merge off-platform holdings from `investor-context.md` into the portfolio JSON so all downstream subagents see a unified portfolio.

**If using a cached snapshot that already contains off-platform positions** (check for `off_platform` key in `balances`): skip this step. The cached snapshot is already enriched.

**Otherwise:**

1. Read `SKILL_DIR/references/investor-context.md`. Parse the Off-Platform Holdings section to extract: precious metals (type, quantity), cryptocurrency (type, quantity), private equity/options (name, quantity, FMV), real estate (properties, values).

2. **Fetch current spot prices** via WebSearch:
   - Gold spot price per troy oz (USD)
   - Silver spot price per troy oz (USD)
   - Bitcoin spot price (USD)
   - Record the prices and timestamp in the JSON under a `spot_prices` key

3. **Construct off-platform position objects** and append to the `positions` array. Each position uses the same field structure as IB positions, plus `source: "manual"` and `liquidity` fields:

   ```json
   {
     "account": "off_platform",
     "account_label": "Off-Platform",
     "tax_treatment": "no_capital_gains_tax",
     "ticker": "GOLD_PHYSICAL",
     "description": "Physical Gold Bullion",
     "asset_class": "COMMODITY",
     "currency": "USD",
     "position": 4,
     "unit": "oz",
     "market_price": <gold_spot>,
     "market_value": <4 * gold_spot>,
     "average_cost": 0,
     "unrealized_pnl": 0,
     "sector": "Precious Metals",
     "base_market_value": <4 * gold_spot>,
     "base_unrealized_pnl": 0,
     "fx_rate": 1,
     "source": "manual",
     "liquidity": "liquid"
   }
   ```

   Create similar objects for:
   - `SILVER_PHYSICAL`: asset_class `COMMODITY`, sector `Precious Metals`
   - `BTC`: asset_class `CRYPTO`, sector `Cryptocurrency`
   - `PAYWARD_OPTIONS`: asset_class `OPT`, sector `Private Equity / Fintech`, use FMV from investor-context.md as market_price, liquidity `liquid`
   - `REAL_ESTATE_PRIMARY`: asset_class `REAL_ESTATE`, sector `Real Estate`, liquidity `illiquid`
   - `REAL_ESTATE_INVESTMENT`: asset_class `REAL_ESTATE`, sector `Real Estate`, liquidity `illiquid`

   For real estate: use the values from investor-context.md directly (no spot price needed). Tax treatment for real estate: `no_capital_gains_tax` (Swiss private real estate).

4. **Add `off_platform` entry to `balances`:**
   ```json
   "off_platform": {
     "label": "Off-Platform Holdings",
     "nav": <sum of all off-platform liquid positions>,
     "cash": 0,
     "total_positions_value": <sum of all off-platform positions incl. illiquid>,
     "base_currency": "USD",
     "source": "manual",
     "illiquid_value": <sum of real estate positions>
   }
   ```

5. **Update `combined` balances:**
   - Add `ib_nav`: original `total_nav` (IB-only)
   - Add `off_platform_liquid_nav`: sum of off-platform liquid positions (precious metals + crypto + Payward options)
   - Add `liquid_nav`: `ib_nav` + `off_platform_liquid_nav`
   - Add `illiquid_nav`: sum of real estate values
   - Add `total_wealth`: `liquid_nav` + `illiquid_nav`
   - Keep original `total_nav`, `total_cash`, `total_positions_value` for IB-only reference

6. **Recompute `allocations`** to include off-platform positions:
   - `by_asset_class`: add COMMODITY, CRYPTO, OPT, REAL_ESTATE categories. Use `liquid_nav` as denominator for percentage calculations (not IB NAV). Mark each entry with `includes_off_platform: true`.
   - `by_sector`: add Precious Metals, Cryptocurrency, Private Equity / Fintech, Real Estate sectors.
   - `by_currency`: add off-platform USD values to the USD total.
   - `by_geography`: add off-platform under "Other" or appropriate geography.
   - `by_account`: add `off_platform` account entry.

7. **Recompute `concentration_flags`** on the full portfolio using `liquid_nav` as the denominator. Flag any single position or sector exceeding 10% of liquid NAV. Include off-platform positions in this check.

8. **Add `spot_prices` to the JSON:**
   ```json
   "spot_prices": {
     "gold_usd_oz": <price>,
     "silver_usd_oz": <price>,
     "btc_usd": <price>,
     "fetched_at": "<ISO timestamp>"
   }
   ```

9. **Save** the enriched JSON to the same file path (overwriting the IB-only version). Apply `chmod 600`.

**Validation:** Verify that `combined.liquid_nav` > `combined.ib_nav` (off-platform adds value). If spot price fetching fails for any asset, use the most recent known price from a previous portfolio-summary JSON if available, or fall back to the FMV in investor-context.md. Log which prices are stale.

### Step 3: Determine mode and resolve inputs

Examine the user's input to determine the analysis mode:

**Two inputs provided -> Comparison Mode:**
- For each input: determine if it is an MD file path or a YouTube URL
- For MD files: read the content
- For YouTube URLs: invoke the `yt-transcript` skill to extract the transcript. Use the transcript content (not the summary).
- If any single resolved input exceeds 10,000 words: compress it into a structured summary preserving all material claims, data points, and conclusions. Remove repetition and filler. Note compression in the output header.
- Save as `OUTPUT_DIR/0-thesis-inputs/thesis-input-a-{YYYY-MM-DD-HH-MM-SS}.md` and `OUTPUT_DIR/0-thesis-inputs/thesis-input-b-{YYYY-MM-DD-HH-MM-SS}.md`
- Set mode = "comparison"

**Single MD file provided -> Thesis Mode:**
- Read the MD file content
- Save to `OUTPUT_DIR/0-thesis-inputs/thesis-input-{YYYY-MM-DD-HH-MM-SS}.md`
- Set mode = "thesis"

**Single YouTube URL provided -> YouTube Mode:**
- Invoke the `yt-transcript` skill to extract the transcript
- Save transcript content to `OUTPUT_DIR/0-thesis-inputs/thesis-input-{YYYY-MM-DD-HH-MM-SS}.md`
- Set mode = "youtube"

**No input -> Market Scan Mode:**
- No thesis input file created
- Set mode = "scan"

YouTube URL patterns to match: `youtube.com/watch?v=`, `youtu.be/`, `youtube.com/embed/`, `youtube.com/shorts/`

If YouTube transcript extraction fails: report the error, offer to continue with Market Scan mode instead.

### Step 4: Check research cache

Look for existing `market-research-cache-*.md` files in `OUTPUT_DIR/1-market-research/`.

- Find the most recent one by filename timestamp
- Parse the timestamp from the filename
- If the file exists and is within `RESEARCH_CACHE_TTL_HOURS` (default 6 hours): mark research as cached, record the cache file path and age. Skip to Step 5.5.
- If no valid cache exists, cache is expired, or user requested `force_fresh_research`: proceed to Step 5.

Cache cleanup: delete any `market-research-cache-*.md` files older than `RESEARCH_CACHE_MAX_AGE_HOURS` (24 hours).

### Step 5: Dispatch Subagent 1 - Market Researcher

Generate the output file path: `OUTPUT_DIR/1-market-research/market-research-cache-{YYYY-MM-DD-HH-MM-SS}.md`

Dispatch the `market-researcher` subagent via the Agent tool:

```
subagent_type: "market-researcher"
model: sonnet
```

Prompt the subagent with:
- Path to the portfolio summary file (from Step 2)
- Path to investor-context.md (`SKILL_DIR/references/investor-context.md`)
- Output file path for the research cache
- Instruction to follow the methodology in its agent definition

After completion:
- Verify the output file exists and is non-empty
- If subagent failed or output missing: inform user, offer to retry or continue without fresh research (use stale cache if available, otherwise abort)

### Step 5.5: Data Quality Gate

Read the market research output file (from Step 5 or cache from Step 4).
Find the `## Data Quality Assessment` section.

- Parse the status field: `NORMAL` or `LOW-CONFIDENCE`
- If `LOW-CONFIDENCE`: log warning. Record the status and degraded domains.
  Include `data_quality: "LOW-CONFIDENCE"` and the list of degraded domains
  in prompts to all downstream subagents. Do NOT abort the pipeline.
- If `NORMAL`: proceed normally.
- If Data Quality Assessment section is not found (e.g., stale cache from
  before this feature): treat as `NORMAL` with a note.

Also extract and record:
- Dominant regime classification and probability (from Section 2)
- Credit cycle phase (from Section 3)
These will be included in the chat summary (Step 10).

### Step 5.6: Dispatch Subagent 2 - Opportunity Scorer

Generate the output file path: `OUTPUT_DIR/2-opportunity-scoring/opportunity-scoring-{YYYY-MM-DD-HH-MM-SS}.md`

Dispatch the `opportunity-scorer` subagent via the Agent tool:

```
subagent_type: "opportunity-scorer"
model: sonnet
```

Prompt the subagent with:
- Path to market research cache file (from Step 5 or Step 4)
- Path to the portfolio summary file (from Step 2)
- Path to investor-context.md (`SKILL_DIR/references/investor-context.md`)
- Data quality status (from Step 5.5)
- Output file path for the opportunity scoring report
- Instruction to follow the methodology in its agent definition

After completion:
- Verify the output file exists and is non-empty
- If subagent failed or output missing: WARN but do NOT abort the pipeline.
  The impact-analyst and recommendation-engine can operate without
  opportunity data. Log: "Opportunity scoring failed. Pipeline continues
  with portfolio-only analysis." Set opportunity_scoring_path to null.

### Step 6: Check for resumable pipeline state

Before dispatching the impact-analyst:
- If a valid `impact-analysis-*.md` exists in `OUTPUT_DIR/3-impact-analysis/` from a recent run (same portfolio snapshot timestamp, less than 1 hour old): skip to Step 8 (recommendation-engine). Log: "Resuming pipeline from stage 4 using existing impact analysis."
- Otherwise: proceed to Step 7.

Note: if resuming, the existing impact analysis may not have the New
Opportunity Overlap Assessment (Step 2.5) if opportunity scoring was
not available during the original run. If opportunity scoring is now
available but was not during the cached impact analysis, do NOT resume.
Re-run the impact-analyst to incorporate the opportunity data.

### Step 7: Dispatch Subagent 3 - Impact Analyst

Generate the output file path: `OUTPUT_DIR/3-impact-analysis/impact-analysis-{YYYY-MM-DD-HH-MM-SS}.md`

Dispatch the `impact-analyst` subagent via the Agent tool:

```
subagent_type: "impact-analyst"
model: opus
```

Prompt the subagent with:
- Path to market research cache file
- Path to opportunity scoring file (from Step 5.6, or note that it is unavailable)
- Path to thesis input file(s) (if thesis/youtube/comparison mode)
- Path to the portfolio summary file (from Step 2)
- Path to investor-context.md (`SKILL_DIR/references/investor-context.md`)
- Path to analysis-framework.md (`SKILL_DIR/references/analysis-framework.md`)
- Mode identifier (thesis/youtube/scan/comparison)
- Data quality status (from Step 5.5)
- Output file path for the impact analysis
- Instruction to follow the methodology in its agent definition and in analysis-framework.md

After completion:
- Verify the output file exists and is non-empty
- If subagent failed or output missing: abort pipeline. Report which stage failed. Note that research cache and opportunity scoring are preserved for retry.

### Step 7.5: Fetch Hedging Market Data

After the impact-analyst completes and before dispatching the recommendation-engine, fetch live options and market data for hedging instruments. This data enables the recommendation-engine to build a precise hedge strategies with real pricing.

**7.5.1: Determine the hedging universe**

Read the impact analysis output file (from Step 7). Parse the Risk Assessment and Correlation and Cluster Analysis sections. Identify:
- The top 3-5 risk factors (from the five risk dimensions)
- Concentrated sectors and correlation clusters
- Key directional exposures (USD, rates, specific sectors)

Use the mapping table below to select which instruments need option chain and market data:

| Risk / Exposure | Put Chain Candidates | Inverse ETF Snapshots | Safe Haven Snapshots |
|---|---|---|---|
| Broad US equity | SPY, QQQ | SH, SQQQ | GLD, TLT |
| Technology / AI | XLK, QQQ | SQQQ | - |
| Semiconductors | SMH, SOXX | SOXS | - |
| Energy | XLE | ERY | - |
| Emerging markets | EEM, VWO | EUM | - |
| USD depreciation | UUP | - | FXE, GLD |
| Interest rate rise | TLT | TBT | SGOV |
| Small cap | IWM | RWM | - |

**Always fetch:** SPY put chain (broad market hedge) and VIX snapshot (vol regime context).
**Select additional instruments** based on the actual risk profile from the impact analysis. Aim for 3-6 option chains total (not all rows above). Only fetch instruments relevant to the portfolio's identified risks.

**7.5.2: Select expiry months**

For each put chain candidate, fetch 3 expiry tenors:
- **Near-term:** ~1 month out from today
- **Medium-term:** ~3 months out
- **Far-term:** ~6 months out

Convert these to YYYYMM format. If a specific month is not available (check the `option_months` returned by the conid search), use the nearest available month.

**7.5.3: Fetch option chains**

For each selected underlying and expiry month, call `ib_option_chain`:
```
ib_option_chain(
  underlying=<symbol>,
  expiry_month=<YYYYMM>,
  right="P",          # puts for downside hedges
  strike_range_pct=20  # strikes within 20% of current price
)
```

For safe haven calls (GLD, TLT, FXE): use `right="C"`.

Make calls sequentially (each call involves multiple IB API requests internally). Log progress.

**7.5.4: Fetch market snapshots**

Call `ib_market_snapshot` with all relevant inverse ETFs and context symbols in a single batch:
```
ib_market_snapshot(
  symbols=["VIX", <selected inverse ETFs>, <selected safe havens>]
)
```

**7.5.5: Assemble and save hedge data**

Combine all fetched data into a single JSON structure:

```json
{
  "fetch_timestamp": "<ISO timestamp>",
  "risk_factors_identified": ["<top risks from impact analysis>"],
  "vix": {"price": <float>, "context": "<low/normal/elevated/high based on level>"},
  "option_chains": {
    "<SYMBOL>_<YYYYMM>_<P|C>": {
      "underlying": "<symbol>",
      "underlying_price": <float>,
      "expiry_month": "<YYYYMM>",
      "right": "<P|C>",
      "options": [
        {"strike": <float>, "bid": <float>, "ask": <float>, "mid": <float>,
         "implied_vol": <float>, "delta": <float>, "theta": <float>,
         "gamma": <float>, "vega": <float>, "volume": <float>,
         "open_interest": <float>}
      ]
    }
  },
  "inverse_etfs": {
    "<SYMBOL>": {
      "price": <float>, "volume": <float>,
      "expense_ratio": <float>, "leverage": <int>,
      "tracked_index": "<string>"
    }
  },
  "safe_havens": {
    "<SYMBOL>": {"price": <float>, "volume": <float>}
  },
  "data_quality": {
    "chains_requested": <int>,
    "chains_with_data": <int>,
    "chains_empty": ["<symbols with no data>"],
    "snapshot_symbols_resolved": <int>,
    "snapshot_symbols_failed": ["<symbols that failed>"]
  }
}
```

VIX context thresholds: <15 = "low", 15-20 = "normal", 20-30 = "elevated", >30 = "high".

**IB Client Portal Gateway data limitations (apply to both option chains and market snapshots):**

- **`implied_vol` is reported as a negative number** by the CP Gateway API. Take `abs(implied_vol)` before storing in the hedge-data JSON. A value of -0.221 means IV = 22.1%.
- **`theta` and `vega` are always null.** The CP Gateway snapshot endpoint does not return these greeks. Omit them from the hedge-data JSON or set to null. The recommendation-engine must not rely on theta/vega from this data; it should estimate theta from time decay if needed.
- **`open_interest` is always null.** The snapshot endpoint does not provide open interest data. Omit or set to null.

When assembling the hedge-data JSON, apply the `abs()` fix to `implied_vol` values. Leave null fields as null rather than inventing values.

Save to `OUTPUT_DIR/3-hedge-data/hedge-data-{YYYY-MM-DD-HH-MM-SS}.json` with `chmod 600`.

**7.5.6: Error handling**

- If IB gateway is not authenticated: skip Step 7.5 entirely. Set `hedge_data_path` to null. Log: "Hedge data unavailable: gateway not authenticated. hedge strategies will use estimated data." The recommendation-engine will fall back to WebSearch-based estimates.
- If individual option chains fail: continue with available data. Note failures in `data_quality`.
- If VIX snapshot fails: note in data_quality, recommendation-engine will fetch via WebSearch.
- If all option chains fail: save the JSON with empty `option_chains`. The recommendation-engine's hedge strategies will note "live options data unavailable" and use directional estimates.

### Step 8: Dispatch Subagent 4 - Recommendation Engine

Generate the output file path: `OUTPUT_DIR/4-portfolio-analysis/portfolio-analysis-{YYYY-MM-DD-HH-MM-SS}.md`

Check for previous analysis: look for existing `portfolio-analysis-*.md` files in `OUTPUT_DIR/4-portfolio-analysis/`. Find the most recent one (if any) for delta analysis.

Dispatch the `recommendation-engine` subagent via the Agent tool:

```
subagent_type: "recommendation-engine"
model: opus
```

Prompt the subagent with:
- Path to impact analysis file
- Path to market research cache file
- Path to opportunity scoring file (from Step 5.6, or note that it is unavailable)
- Path to hedge data file (from Step 7.5, or note that it is unavailable)
- Path to the portfolio summary file (from Step 2)
- Path to investor-context.md (`SKILL_DIR/references/investor-context.md`)
- Path to output-template.md (`SKILL_DIR/references/output-template.md`)
- Path to previous portfolio-analysis-*.md (if exists)
- Mode identifier (thesis/youtube/scan/comparison)
- Output file path for the final analysis
- Instruction to follow the methodology in its agent definition and format per output-template.md

After completion:
- Verify the output file exists and is non-empty
- If subagent failed or output missing: abort. Report error. Note that research cache, opportunity scoring, and impact analysis are preserved for retry.

### Step 8.5: Escalation Check

Read the recommendation-engine output file from Step 8.
Find the Escalation Flags section (located in the Appendix).

**If "No escalation flags triggered":** proceed to Step 9.

**If escalation flags exist and `escalation_retry_count < MAX_ESCALATION_RETRIES` (default 1):**

For each escalation flag:
1. Parse the flag: breach type, upstream stage to re-run, modified constraint
2. Re-dispatch the specified upstream subagent with the modified constraint
   appended to its prompt. Use a `-pass2` suffix on the output filename
   (e.g., `opportunity-scoring-{timestamp}-pass2.md`) to avoid overwriting
   the original.
3. Then re-dispatch all downstream subagents in sequence (each receiving
   the updated upstream output). Use `-pass2` suffix on all filenames.

Increment `escalation_retry_count`.

After the re-run completes, check the new recommendation-engine output
for escalation flags again. If flags are resolved: use the pass-2 output
as the final analysis. If flags remain: proceed to Step 9 with the
pass-2 output, noting in the chat summary that escalation flags remain
unresolved after one retry.

**If escalation flags exist but `escalation_retry_count >= MAX_ESCALATION_RETRIES`:**
- Log: "Escalation flags remain after {MAX_ESCALATION_RETRIES} retry(s). Proceeding with flagged output."
- Proceed to Step 9 with the latest output.

### Step 9: Present output

Read the final analysis file.

Check investor-context.md modification date:
- Get the last-modified timestamp of `SKILL_DIR/references/investor-context.md`
- If older than 90 days: include staleness warning in chat summary

Present a concise chat summary covering:
- Mode used and research freshness (fresh or cached, with age)
- Regime classification: dominant regime and probability (from Step 5.5)
- Data quality status: NORMAL or LOW-CONFIDENCE (from Step 5.5)
- Credit cycle phase (from Step 5.5)
- Top 3-5 findings / key takeaways from the analysis
- High-priority recommendations (action, ticker, account, size)
- Any escalation flags and whether they were resolved
- Any urgent flags (concentration risk, thesis invalidation signals)
- Staleness warning for investor-context.md if applicable
- Full file path to the complete analysis MD

The chat summary is not a replacement for the full report. It exists so the user immediately knows if something needs attention without opening the file.

### Step 10: Cleanup intermediate files

Delete old intermediate files from `OUTPUT_DIR` subdirectories:
- `0-thesis-inputs/thesis-input-*.md` files older than `INTERMEDIATE_FILE_MAX_AGE_DAYS` (7 days)
- `3-impact-analysis/impact-analysis-*.md` files older than `INTERMEDIATE_FILE_MAX_AGE_DAYS` (7 days)
- `3-hedge-data/hedge-data-*.json` files older than `INTERMEDIATE_FILE_MAX_AGE_DAYS` (7 days)
- `2-opportunity-scoring/opportunity-scoring-*.md` files older than `INTERMEDIATE_FILE_MAX_AGE_DAYS` (7 days)
- `0-portfolio-snapshots/portfolio-summary-*.json` files older than `INTERMEDIATE_FILE_MAX_AGE_DAYS` (7 days)
- Research cache files are cleaned in Step 4 (24-hour policy)

Keep the most recent set of each for debugging.

## Error Handling

| Error | Action |
|-------|--------|
| MCP server not available | Tell user to check ib-connect MCP configuration |
| Gateway not running | Call ib_start_gateway, prompt user for auth |
| Auth expired | Call ib_reauthenticate, prompt user to complete login |
| Zero NAV across all accounts | Stop. Report data issue. |
| Spot price fetch fails | Use previous snapshot price or investor-context FMV. Log staleness. |
| yt-transcript skill missing | Tell user to install yt-transcript skill |
| YouTube transcript extraction fails | Report error, offer Market Scan mode instead |
| Market researcher fails | Inform user, offer retry or use stale cache |
| Opportunity scorer fails | WARN only, continue pipeline without opportunity data |
| Impact analyst fails | Stop pipeline, report stage failure, note preserved outputs |
| Recommendation engine fails | Stop pipeline, report stage failure, note preserved outputs |
| Subagent output missing/empty | Stop pipeline (except opportunity-scorer: warn only) |
| Research cache expired | Dispatch fresh research (normal flow) |
| Data quality LOW-CONFIDENCE | Continue with warning, downstream agents cap conviction |
| Escalation flags triggered | Re-run upstream stage once, then proceed regardless |
| Hedge data fetch fails (gateway) | Skip Step 7.5, set hedge_data_path to null, continue pipeline |
| Hedge data fetch fails (partial) | Save partial data, note failures in data_quality field |
| Option chain returns no data | Include in hedge-data JSON with empty options, note in data_quality |
| investor-context.md missing | Stop. Tell user to create the file. |
| investor-context.md stale (90+ days) | Warn in chat summary, continue with analysis |

## Notes

- The orchestrator itself is lightweight. It validates inputs, checks caches, enriches portfolio data with off-platform holdings, dispatches subagents, and presents results. All heavy reasoning happens in the subagents.
- The portfolio-summary JSON is enriched in Step 2.5 to include off-platform holdings as first-class positions. Subagents see a unified portfolio and do not need to read investor-context.md separately for off-platform data.
- Subagents receive file paths, not file contents. This keeps the orchestrator's context window clean.
- Each subagent runs in its own isolated context window via the Agent tool.
- Subagents run sequentially because each depends on the previous stage's output (except the escalation loop which re-runs specific stages).
- The market-researcher and opportunity-scorer subagents run on Sonnet (cost-efficient for web search + synthesis). The impact-analyst and recommendation-engine run on Opus (deep reasoning).
- All intermediate and output files are saved in per-stage subdirectories under `OUTPUT_DIR` for traceability.
- Portfolio data files should have `chmod 600` permissions (sensitive financial data).
