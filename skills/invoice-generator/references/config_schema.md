# Invoice Config Schema

The generator reads a JSON config file describing the invoice. All fields below are listed with their type and whether they're required.

## Top-level fields

| Field | Type | Required | Description |
|---|---|---|---|
| `currency` | string | no | Currency symbol/code shown next to amounts. Defaults to `"CHF"`. Examples: `"EUR"`, `"USD"`, `"GBP"` |
| `number_prefix` | string | no | Prefix for auto-generated invoice numbers. Defaults to `"BL"`. Result: `{PREFIX}-YYYY-MM-NNN` |
| `supplier` | object | yes | Who is sending the invoice (the "from") |
| `recipient` | object | yes | Who the invoice is billed to |
| `invoice` | object | yes | Invoice metadata (number, date, etc.) |
| `service` | object | yes | Description of what was provided |
| `hours` | number | conditional | Hours worked. Required if `rate` is set |
| `rate` | number | conditional | Hourly rate. Required if `hours` is set |
| `total` | number | conditional | Flat total. Use instead of hours/rate for fixed-price work |
| `vat` | object | no | VAT treatment. Defaults to `{"mode": "none"}` |
| `payment` | object | no | Payment details (IBAN, BIC, etc.) |
| `amount_paid` | number | no | Amount already paid. Defaults to `0`. Balance due = gross - amount_paid |
| `notes` | string | no | HTML content for the left footer box. Empty string leaves it blank |
| `appendix_title` | string | no | Title for the appendix page. Defaults to `"Work Breakdown."` |
| `appendix_subtitle_suffix` | string | no | Extra sentence appended to appendix subtitle |
| `line_items` | array | no | Optional itemised breakdown. If present, triggers an appendix page |

You must provide either (`hours` AND `rate`) OR `total`. Providing both is allowed; `hours * rate` wins and should match `total` if you provide both.

## `supplier` object

```json
{
  "name": "Acme Consulting GmbH",
  "address": ["Musterstrasse 42", "8001 Zürich", "Switzerland"],
  "vat": "CHE-123.456.789 MWST"
}
```

| Field | Type | Required |
|---|---|---|
| `name` | string | yes |
| `address` | array of strings | yes - one line per array element |
| `vat` | string | no - shown as "VAT: ..." under the address |

## `recipient` object

```json
{
  "name": "Globex Corp AG",
  "address": ["Beispielweg 10", "4001 Basel", "Switzerland"]
}
```

| Field | Type | Required |
|---|---|---|
| `name` | string | yes |
| `address` | array of strings | yes |

## `invoice` object

```json
{
  "number": "AC-2026-03-003",
  "date": "April 7, 2026",
  "service_period": "March 2 - 31, 2026",
  "due_date": "April 30, 2026"
}
```

| Field | Type | Required |
|---|---|---|
| `number` | string | yes (can be a placeholder if using `--auto-number`) - also used as payment reference |
| `date` | string | yes - formatted as you want it displayed |
| `service_period` | string | no - e.g., "March 2 - 31, 2026" |
| `due_date` | string | no - formatted as you want it displayed |

## `service` object

```json
{
  "description": "Strategic consulting services",
  "subtitle": "Per Contractor Agreement dated February 26, 2026"
}
```

| Field | Type | Required |
|---|---|---|
| `description` | string | yes - main line in the services table |
| `subtitle` | string | no - smaller grey text below the description |

## `vat` object

```json
{
  "mode": "inclusive",
  "rate": 0.081
}
```

| Field | Type | Required |
|---|---|---|
| `mode` | string | yes - one of `"inclusive"`, `"exclusive"`, `"none"` |
| `rate` | number | conditional - decimal fraction (0.081 = 8.1%). Required for inclusive/exclusive |

**Mode semantics:**
- `inclusive` - the quoted amount contains VAT. Net = gross / (1 + rate). Use when a contract says "fee inclusive of all taxes"
- `exclusive` - the quoted amount is pre-tax. Gross = net * (1 + rate). Default for most B2B contracts
- `none` - no VAT line shown. Use for non-registered suppliers, zero-rated supplies, or reverse-charge B2B services

## `payment` object

```json
{
  "account_holder": "Acme Consulting GmbH",
  "iban": "CH93 0076 2011 6238 5295 7",
  "bic": "UBSWCHZH80A"
}
```

| Field | Type | Required |
|---|---|---|
| `account_holder` | string | no |
| `iban` | string | no - format with spaces for readability |
| `bic` | string | no |

The invoice number is automatically used as the payment reference line.

## `line_items` array

```json
[
  {"date": "Mar 2, 2026", "hours": 3.0, "description": "Kickoff meeting"},
  {"date": "Mar 3, 2026", "hours": 1.5, "description": "Design review"}
]
```

| Field | Type | Required |
|---|---|---|
| `date` | string | recommended |
| `hours` | number | recommended - appears in the Hours column and totalled at the bottom |
| `description` | string | yes |

If `line_items` is provided, a second page (Appendix) is added with a table of all items. If no line items have `hours`, the Hours column is hidden and the date+description fill the width.

## Full example

See `examples/wyden_example.json` for a complete hours-based VAT-inclusive invoice with a 45-item appendix, or `examples/minimal_example.json` for a minimal flat-total invoice without VAT or appendix.
