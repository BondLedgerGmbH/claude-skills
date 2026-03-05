---
name: ib-analyseportfolio
description: >
  Analyse an investment portfolio held across two Interactive Brokers accounts
  against a specific thesis, research, or market conditions. Operates in four
  modes: (1) Thesis mode - user provides an MD file with research, macro thesis,
  or transcript analysis; (2) YouTube mode - user provides a YouTube URL,
  the skill extracts the transcript via the yt-transcript skill (supports
  auto-translated and non-English videos) and analyses the portfolio against
  the video content; (3) Market scan mode - no input provided, the skill
  performs a broad web search for current macro/market developments and analyses
  the portfolio against those findings; (4) Comparison mode - user provides
  two inputs (any combination of MD files and/or YouTube URLs), the skill
  analyses both perspectives against the portfolio and highlights where they
  agree, conflict, and what that means for positioning. Use this skill when
  the user wants to: assess how news/research/events/videos impact their
  portfolio, get portfolio-wide risk analysis, check concentration or currency
  exposure, get tax-aware recommendations across corporate and personal accounts,
  run a broad market scan, or compare two opposing views against their holdings.
  Also trigger when the user mentions "portfolio analysis", "position review",
  "market impact on my holdings", "what should I do with my portfolio", "analyse
  this video against my portfolio", "compare these two views", or references
  their IB accounts in an investment context.
---

# IB Portfolio Analysis Engine

## Configuration

```
RESEARCH_CACHE_TTL_HOURS = 6
PORTFOLIO_CACHE_TTL_MINUTES = 60
INTERMEDIATE_FILE_MAX_AGE_DAYS = 7
RESEARCH_CACHE_MAX_AGE_HOURS = 24
MAX_ESCALATION_RETRIES = 1
DATA_QUALITY_UNAVAILABLE_THRESHOLD_PCT = 20
PROJECT_DIR = <YOUR_PROJECT_DIR>
OUTPUT_DIR = <YOUR_PROJECT_DIR>/output/ib-analysis
SKILL_DIR = <YOUR_PROJECT_DIR>/.claude/skills/ib-analyseportfolio
AGENTS_DIR = <YOUR_PROJECT_DIR>/.claude/agents
```

> **Setup required:** Replace `<YOUR_PROJECT_DIR>` with your actual project
> directory (e.g., `/home/user/projects/my-project`). This is the root
> directory where Claude Code runs. The skill will not work without valid paths.

## Output Directory Structure

All intermediate and final files are organised in per-stage subdirectories:

```
OUTPUT_DIR/
├── 0-portfolio-snapshots/     ← portfolio-summary-{timestamp}.json
├── 0-thesis-inputs/           ← thesis-input-{timestamp}.md
├── 1-market-research/         ← market-research-cache-{timestamp}.md
├── 2-opportunity-scoring/     ← opportunity-scoring-{timestamp}.md
├── 3-impact-analysis/         ← impact-analysis-{timestamp}.md
└── 4-portfolio-analysis/      ← portfolio-analysis-{timestamp}.md (final output)
```

## Dependencies

- MCP server `ib-connect` must be configured and available (provides `ib_status`, `ib_start_gateway`, `ib_portfolio_summary` tools)
- `yt-transcript` skill must be installed for YouTube mode and comparison mode with YouTube URLs
- Four custom subagents in `.claude/agents/`: `market-researcher.md`, `opportunity-scorer.md`, `impact-analyst.md`, `recommendation-engine.md`

## Execution Flow

### Step 1: Ensure output directory exists

Create `OUTPUT_DIR` and all subdirectories if they do not exist:
`0-portfolio-snapshots/`, `0-thesis-inputs/`, `1-market-research/`,
`2-opportunity-scoring/`, `3-impact-analysis/`, `4-portfolio-analysis/`.

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
Find the `## Escalation Flags` section.

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
| investor-context.md missing | Stop. Tell user to create the file. |
| investor-context.md stale (90+ days) | Warn in chat summary, continue with analysis |

## Notes

- The orchestrator itself is lightweight. It validates inputs, checks caches, dispatches subagents, and presents results. All heavy reasoning happens in the subagents.
- Subagents receive file paths, not file contents. This keeps the orchestrator's context window clean.
- Each subagent runs in its own isolated context window via the Agent tool.
- Subagents run sequentially because each depends on the previous stage's output (except the escalation loop which re-runs specific stages).
- The market-researcher and opportunity-scorer subagents run on Sonnet (cost-efficient for web search + synthesis). The impact-analyst and recommendation-engine run on Opus (deep reasoning).
- All intermediate and output files are saved in per-stage subdirectories under `OUTPUT_DIR` for traceability.
- Portfolio data files should have `chmod 600` permissions (sensitive financial data).
