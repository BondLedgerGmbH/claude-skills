---
name: invoice-generator
description: Generate professional PDF invoices using the Modern Black template. Use this skill whenever the user asks to create, generate, draft, or produce an invoice, bill, or similar payment document - even if they don't explicitly say "invoice" (phrases like "bill my client", "charge for my hours", "send my client March work", "create a receipt for consulting"). The skill handles VAT (inclusive, exclusive, or none), optional work-item breakdowns in an appendix, and produces a branded PDF with a dark navy frame, oversized serif wordmark, and clean totals stack. Trigger this skill for any invoice-generation request, not just when the user provides a template.
---

# Invoice Generator

This skill generates polished PDF invoices using a pre-built "Modern Black" template. The visual design is locked in (dark navy frame, Times serif wordmark, borderless line-item table) - the skill's job is to gather the user's data, assemble a JSON config, run the generator script, and return the PDF.

## When to use this skill

Trigger on any request to create an invoice or similar billing document:
- "Generate an invoice for ..."
- "Bill my client for ..."
- "Create a PDF invoice showing ..."
- "I need to send X an invoice for Y hours of work"
- "Turn this timesheet into an invoice"

Also trigger when the user uploads a timesheet, time log, or work breakdown and asks to get paid / bill someone / send a statement - these are implicit invoice requests.

## Workflow

### Step 0: Check for saved profiles

Before asking the user for supplier/recipient/payment/VAT details, check the `profiles/` directory for previously saved combinations:

```bash
ls <skill-path>/profiles/*.json
```

If profiles exist, read them and present a short summary to the user, e.g.:

> I found these saved invoice profiles:
> 1. **Acme Consulting GmbH → Globex Corp AG** — CHF, VAT inclusive 8.1%, IBAN ending ...5295 7
> 2. **Acme Consulting GmbH → Client Co** — EUR, no VAT, IBAN ending ...0130 00
>
> Use one of these, or provide new details?

If the user picks a profile, load its `supplier`, `recipient`, `payment`, `vat`, and `currency` fields into the config. Also apply `default_service` (as `service.description`) and `default_rate` (as `rate`) if present in the profile. The user then only needs to provide hours, dates, and optional line items — or override any defaults.

When presenting a profile, mention the defaults so the user knows what will be applied:

> 1. **Acme Consulting GmbH → Globex Corp AG** — CHF 150/hour, Strategic consulting services, VAT inclusive 8.1%, IBAN ending ...5295 7

If no profiles exist, or the user wants to use new details, proceed to Step 1 as normal.

**After generating an invoice with new details**, check whether the supplier+recipient+payment+VAT combination already exists as a profile. If not, ask the user whether they'd like to save it for future use. If yes, write a new JSON file to `profiles/` named `{supplier_slug}_to_{recipient_slug}.json` using the same structure as existing profiles. Include a `profile_name` field formatted as `"{Supplier} → {Recipient}"`.

**Updating profiles:** If the user provides details that differ from a loaded profile (e.g., new address, new IBAN), use the new details for the invoice and ask whether the profile should be updated to reflect the change. Overwrite the profile JSON if yes.

### Step 1: Gather inputs

Ask the user for anything not already provided (either from a profile or from conversation context). The minimum viable invoice needs:

**Required:**
- **Supplier** (who is sending the invoice): name, address lines, optionally VAT number
- **Recipient** (bill to): name, address lines
- **Invoice metadata**: invoice number (auto-generated if not provided — see below), invoice date, due date
- **Service**: short description of what was provided
- **Amount**: either (hours + rate) OR a flat total
- **Payment info**: at minimum an IBAN or account number so the recipient can pay

**Optional:**
- Service period (e.g., "March 2 - 31, 2026")
- VAT treatment (inclusive / exclusive / none - see VAT section below)
- Currency (defaults to CHF; set to EUR, USD, GBP, etc. as needed)
- Amount paid (for partial payments — balance due = gross - amount paid; defaults to 0)
- Itemised work breakdown for the appendix (dates + hours + descriptions)
- Service subtitle (e.g., "Per Contract dated ...")
- Notes for the left footer box

Check the conversation first. If the user uploaded a contract, timesheet, or prior invoice, mine it for supplier/recipient/rate/IBAN details before asking. Don't make the user re-type information that's already in context.

If asking multiple small questions, batch them into a single message. For choices (e.g., VAT mode), present numbered options the user can pick from.

### Step 2: Handle VAT correctly

VAT handling is the most common source of errors. Three modes:

- **`inclusive`** - the agreed rate already contains VAT. The gross is what the client pays; VAT is extracted from within. Formula: `net = gross / (1 + vat_rate)`. Use this when a contract says "fee is inclusive of all taxes" or similar.
- **`exclusive`** - the agreed rate is pre-tax. VAT is added on top. Formula: `gross = net * (1 + vat_rate)`. This is the common case for most B2B invoices where the rate was negotiated net.
- **`none`** - no VAT line on the invoice. Use when the supplier isn't VAT-registered, the supply is zero-rated, or the transaction is reverse-charge (foreign B2B service).

**If the user is VAT-registered and you don't know which mode applies, ASK. Don't guess.** A wrong mode can silently cost the user hundreds to thousands in the wrong direction.

Common VAT rates to recognise: Switzerland 8.1%, Germany 19%, France 20%, UK 20%, Austria 20%, Italy 22%.

### Step 2b: Invoice numbering

Invoice numbers are auto-generated by default using the format `{PREFIX}-{YYYY}-{MM}-{NNN}`:
- `{PREFIX}` defaults to `"BL"` but can be set per-invoice via `number_prefix` in the config or profile. Useful when invoicing from different entities.
- `{YYYY}` and `{MM}` are derived from the **service period** (or invoice date as fallback) — not the current date. An invoice for March services generated in April gets a `03` month code.
- `{NNN}` is a zero-padded counter starting at 001, incrementing per month
- The script scans `~/invoice-generator-output/` for existing invoices matching that year-month and picks the next number

To use auto-numbering, pass `--auto-number` to the script and set `invoice.number` to any placeholder (it will be overwritten). If the user provides an explicit invoice number, use that instead and do NOT pass `--auto-number`.

### Step 3: Build the config JSON

Assemble a config matching the schema in `references/config_schema.md`. Save it to a temporary path (e.g., `/tmp/invoice_config.json`).

A complete example with all fields is in `examples/wyden_example.json`. A minimal example without VAT or appendix is in `examples/minimal_example.json`. Read whichever one is closer to the user's case.

### Step 4: Run the generator

Execute the script from the skill directory. The `--output` flag is optional — if omitted, the PDF is saved to `~/invoice-generator-output/invoice-{invoice_number}.pdf` automatically.

```bash
<skill-path>/.venv/bin/python3 <skill-path>/scripts/generate_invoice.py \
    --config /tmp/invoice_config.json \
    --auto-number
```

Or with an explicit invoice number and output path:

```bash
<skill-path>/.venv/bin/python3 <skill-path>/scripts/generate_invoice.py \
    --config /tmp/invoice_config.json \
    --output ~/invoice-generator-output/invoice-CUSTOM-001.pdf
```

The script prints a JSON summary with page count and computed totals. A copy of the config JSON is saved alongside the PDF (same name, `.json` extension) for audit and regeneration.

**Dry-run mode:** To preview totals without generating a PDF, add `--dry-run`:

```bash
<skill-path>/.venv/bin/python3 <skill-path>/scripts/generate_invoice.py \
    --config /tmp/invoice_config.json \
    --auto-number --dry-run
```

This prints the computed numbers (net, VAT, gross, balance due) and exits. Use this to verify VAT math before committing to a PDF.

**Credit notes:** If the total or hours are negative, the template automatically switches the header label from "INVOICE" to "CREDIT NOTE". Use a negative `total` or negative `hours` in the config.

**List invoices:** To see all generated invoices:

```bash
<skill-path>/.venv/bin/python3 <skill-path>/scripts/generate_invoice.py --list
```

Prints a table with invoice number, date, recipient, gross amount, and whether the PDF exists.

**CSV import:** To auto-populate line items from a timesheet CSV:

```bash
<skill-path>/.venv/bin/python3 <skill-path>/scripts/generate_invoice.py \
    --config /tmp/invoice_config.json \
    --import-csv /path/to/timesheet.csv \
    --auto-number
```

The CSV parser auto-detects delimiter (semicolon, comma, tab), decimal format (comma or dot), column mapping (by header labels or positional fallback), and date formats (DD.MM.YYYY, YYYY-MM-DD, MM/DD/YYYY, English month names). Extracted values are merged into the config — existing config values take precedence over CSV-derived values.

**Regenerate:** To re-render a PDF from a saved config JSON (e.g., after fixing a typo in the JSON):

```bash
<skill-path>/.venv/bin/python3 <skill-path>/scripts/generate_invoice.py \
    --regenerate ~/invoice-generator-output/invoice-BL-2026-03-001.json
```

This reads the JSON, re-runs the generator, and overwrites the PDF at the same path. Use `--output` to write to a different path instead.

### Step 4b: Check for duplicates

Before running the generator, check if a PDF already exists at the target output path:

```bash
ls ~/invoice-generator-output/invoice-{invoice_number}.pdf
```

If a file exists, warn the user and ask whether to overwrite or generate the next sequential number instead. Do not silently create a phantom invoice.

### Step 5: Present and sanity check

Open the PDF for the user (e.g., `open <path>` on macOS). In your message:
- State the key numbers (hours, rate, net, VAT, gross)
- Flag any assumptions you made (VAT mode, currency, date format)
- If the user provided a contract, note any clauses relevant to the invoice (e.g., hours caps, weekday restrictions) that the user should verify before sending

Don't skip the sanity check. Invoices are financial documents - a wrong rate, wrong VAT mode, or wrong IBAN creates real problems.

## Design constraints

The template visual design is fixed and should NOT be modified per-invoice:
- Dark navy (`#2C3E4C`) frame inset 10mm from each edge
- Oversized serif (Times-Roman 28pt) wordmark with "INVOICE" label above
- Dark navy pill in top-right with invoice number and date
- Horizontal rules separating header / line items / footer
- Borderless services table
- Right-aligned totals stack: SUB TOTAL / VAT / TOTAL AMOUNT / AMOUNT PAID / BALANCE DUE
- Two-column footer: left (notes, optional) / right (payment info)
- Page number `N/total` bottom-right inside the frame

If a user asks for design changes (different colors, different layout), either:
1. Explain these are baked into the template, or
2. Edit `assets/template.py` (colors and style constants) and `scripts/generate_invoice.py` (layout) directly. Don't try to pass visual overrides through the config - the config is for data only.

## Quality checks before presenting

Before opening the PDF, verify:
1. **Math adds up**: net + VAT == gross (or gross extracted cleanly for inclusive mode)
2. **All required fields rendered**: supplier, recipient, invoice number, date, amount, IBAN
3. **Line items sum correctly** (if appendix present): sum of item hours == total hours on the invoice line
4. **Currency is consistent** throughout the document
5. **Date format is consistent** (don't mix "April 7, 2026" and "7 Apr 26")

If running locally, rasterize the first page with `pdf2image` and inspect it to catch layout issues (column collisions, text overflow, wrong alignment).

## Reference material

- `references/config_schema.md` - Full JSON config schema with field types and defaults
- `examples/wyden_example.json` - Full example: hours-based, VAT-inclusive, with appendix
- `examples/minimal_example.json` - Minimal example: flat total, no VAT, no appendix
- `assets/template.py` - Template constants (edit here for design tweaks)
- `scripts/generate_invoice.py` - Main generator (edit here for layout tweaks)
- `profiles/*.json` - Saved supplier/recipient/payment/VAT profiles for reuse
