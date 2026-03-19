---
name: execute-trade
description: >
  Execute trades on Interactive Brokers from the CLI. Supports buy/sell
  orders with quantity or cash amount, multiple order types (market, limit,
  stop), and both live and paper trading modes. Use this skill when the
  user wants to execute a trade, place an order, buy or sell a stock,
  or says things like "execute trade", "buy X shares of Y", "sell all Z",
  "place order", "execute recommendation 1". Also trigger when the user
  references executing a specific recommendation from a portfolio analysis.
---

# Execute Trade

## Configuration

- MCP server: `ib-connect` (must be configured and available)
- Default order type: MKT (market)
- Default TIF: DAY
- Default mode: live

## Account Mapping

| User Label | Config Key (Live) | Config Key (Paper) |
|------------|-------------------|--------------------|
| personal   | personal          | personal-paper     |
| corporate  | corporate        | corporate-paper   |

When the user says "account:corporate", map to "corporate" (live) or
"corporate-paper" (paper mode).

## Workflow

### Step 1: Parse the user's intent

Extract from the user's message:
- **Action:** BUY or SELL (REBALANCE is not yet supported — see Future section)
- **Ticker:** Target security symbol
- **Quantity:** One of:
  - Share count (e.g., "50 shares", "50 AVAV", "100")
  - Cash amount (e.g., "$9200", "$9,200 worth")
  - "ALL" (for SELL ALL — liquidate entire position)
- **Account:** "personal" or "corporate" (required)
- **Mode:** "live" (default) or "paper"
- **Order type:** "market" (default), "limit", "stop", "stop-limit"
- **Limit price:** Required for limit and stop-limit orders
- **Stop price:** Required for stop and stop-limit orders
- **TIF:** "DAY" (default), "GTC", "IOC"

If any required field is ambiguous or missing, ask the user. Do NOT guess
the account — always require it explicitly.

If the user requests REBALANCE, respond:
"REBALANCE is not yet supported. Execute sell and buy as separate trades."

#### Handling rec:N (recommendation from portfolio analysis)

If the user says something like "execute recommendation 2", "rec:2", or
"execute rec 2 from the analysis":

1. Find the most recent `portfolio-analysis-*.md` file in
   `{OUTPUT_DIR}/4-portfolio-analysis/`
2. Read the file and find the `## Recommendations` section
3. Locate the Recommendations Summary table (lines starting with `|`)
4. Parse the row matching the requested recommendation number (column 1)
5. Extract fields from the table columns:
   - Column 2: Action (EXIT -> SELL ALL, ADD -> BUY)
   - Column 3: Ticker/Asset
   - Column 4: Account (Corporate -> corporate, Personal -> personal)
   - Column 7: Amount (USD)
   - Column 10: Execute timing
   - Column 11: Entry Condition
6. Pre-fill all parameters from the extracted data
7. Check entry conditions and warn the user if conditions appear unmet
   (e.g., "Entry condition says AVAV below $220 but current price is $225")
8. Still proceed to Step 3 (Preview) — never skip confirmation

### Step 2: Validate gateway and authentication

Map the account label to the config key using the Account Mapping table above.
Apply mode: if `mode:paper`, append `-paper` to the config key.

Call `ib_status(account=<resolved_account>)`.

- If gateway not running: call `ib_start_gateway(account=<resolved_account>)`.
  Tell user to authenticate. Wait for confirmation.
- If auth required: call `ib_reauthenticate(account=<resolved_account>)`.
  Tell user to log in. Wait for confirmation.
- If authenticated: proceed.

### Step 2b: Handle ambiguous tickers

The MCP tools use smart symbol resolution:
1. If the ticker exists in the account's portfolio, the portfolio conid is used automatically.
2. If not in portfolio, IB search is used. The primary listing (most derivative sections) is picked when it clearly leads.
3. If ambiguous (same section count, multiple exchanges), the tool returns `{"error": "ambiguous_symbol", "candidates": [...]}`.

When you get an `ambiguous_symbol` error:
- Present the candidates to the user with exchange names
- Ask which one they want
- Re-call the tool with the `conid` parameter set to the user's choice

Example: CSH2 is listed on both LSE (GBP) and SBF (EUR). If the user already holds CSH2, the portfolio conid is used. Otherwise, ask which exchange.

### Step 3: Preview the order

Call `ib_order_preview` with the parsed parameters.

Map order type strings to API values:
- "market" -> "MKT"
- "limit" -> "LMT"
- "stop" -> "STP"
- "stop-limit" -> "STP_LIMIT"

For SELL ALL: pass `quantity=-1` (the tool resolves the actual position size).
If re-calling after disambiguation: pass the chosen `conid` parameter.

Present the preview to the user in a clear format:

```
ORDER PREVIEW
-------------------------------------
Action:     BUY
Ticker:     AVAV
Quantity:   42 shares
Price:      ~$215.38 (market)
Est. Value: ~$9,046
Commission: ~$1.02
Account:    Personal
Mode:       LIVE (or PAPER)
TIF:        DAY
-------------------------------------
Margin impact: +$X initial, +$Y maintenance
Warnings: [any IB warnings]
```

For cash-based orders, also show:
```
Cash amount: $9,200.00
Last price:  $215.38
Shares:      42 (= floor($9,200 / $215.38))
Actual cost: ~$9,045.96
Remainder:   ~$154.04 (stays as cash)
```

### Step 4: Get user confirmation

Ask the user to confirm. This is MANDATORY — never skip this step.

Use AskUserQuestion with options:
- "Execute order" (proceeds to Step 5)
- "Cancel" (aborts)
- "Modify" (returns to Step 1 with adjustments)

For LIVE mode, include an explicit warning:
"This will execute a REAL trade on your LIVE account."

For PAPER mode, note:
"This is a PAPER trade — no real money involved."

### Step 5: Execute the order

Call `ib_place_order` with the confirmed parameters.

Report the result:

```
ORDER EXECUTED
-------------------------------------
Order ID:   1234567890
Status:     PreSubmitted
Ticker:     AVAV
Side:       BUY
Quantity:   42 shares
Type:       MKT
Account:    Personal (LIVE)
-------------------------------------
```

If the order fails, report the error clearly and suggest next steps.

### Step 6: Post-execution status check

Wait 3 seconds, then call `ib_order_status(account=<account>)` to check
if the order has filled. Report the fill status:

```
ORDER STATUS UPDATE
-------------------------------------
Status:     Filled
Filled:     42 / 42 shares
Avg Price:  $215.40
-------------------------------------
```

If the order is still working (Submitted, PreSubmitted), tell the user
they can check status later or cancel.

### Step 7: Write audit log

After each order attempt (success or failure), append an entry to:
`{OUTPUT_DIR}/order-log.md`

Format:
```markdown
## YYYY-MM-DD HH:MM:SS UTC
- **Action:** BUY 42 AVAV
- **Account:** Personal (live)
- **Order Type:** MKT
- **Order ID:** 1234567890
- **Status:** Filled
- **Source:** Manual (or "Recommendation #2 from portfolio-analysis-YYYY-MM-DD-HH-MM-SS.md")
```

Create the file if it doesn't exist. Always append, never overwrite.

## Error Handling

| Error | Action |
|-------|--------|
| MCP server not available | Tell user to check ib-connect configuration |
| Gateway not running | Start gateway, prompt for auth |
| Auth expired | Reauthenticate, prompt for login |
| Symbol not found | Ask user to verify ticker |
| Ambiguous symbol | Show candidates with exchanges, ask user to choose, re-call with `conid` |
| Insufficient funds | Report available cash, suggest smaller order |
| Order rejected by IB | Report rejection reason verbatim |
| Market closed | Note that order will queue for next session (if GTC) or suggest waiting |
| Cash amount < 1 share | Report minimum order size |
| SELL ALL with no position | Report that no position exists |
| Paper account not configured | Guide user to set up paper trading |

## Safety Rules

1. NEVER place an order without user confirmation (Step 4)
2. NEVER default to live mode if the user said "paper"
3. NEVER guess the account — require explicit specification
4. For SELL ALL: always show the position size being sold in the preview
5. For cash orders: always show the calculated share count and remainder
6. If the user references a portfolio analysis recommendation, extract the
   exact parameters from the recommendation and pre-fill them — but still
   require confirmation
7. Log every order attempt (success or failure) for audit trail

## Future: REBALANCE

REBALANCE is a planned feature that will support selling one position and
buying another in a single workflow, with automatic FX conversion when the
source and target are in different currencies.

**Planned flow:**
1. Sell source ticker (e.g., SGOV in USD)
2. If currencies differ: execute FX conversion (USD -> EUR) using `isCcyConv: true`
3. Buy target ticker (e.g., CSH2 in EUR) with proceeds

**When a user requests REBALANCE before this is implemented:**
Respond: "REBALANCE is not yet supported. Execute sell and buy as separate trades."

**Dependencies for REBALANCE implementation:**
- Currency detection from portfolio data or contract info endpoint
- FX conversion order support (`resolve_fx_conid` already exists in `orders.py`)
- Multi-step execution with partial failure state reporting
