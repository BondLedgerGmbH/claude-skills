#!/usr/bin/env python3
"""
Invoice generator - Modern Black template.

Usage:
    python generate_invoice.py --config <path-to-config.json> --output <path-to-output.pdf>

The config JSON structure is documented in the skill's SKILL.md. Run with --help
for CLI options or see the examples/ directory for sample configs.
"""
import argparse
import json
import re
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.lib import colors

# Make sibling assets/ importable
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SKILL_ROOT / "assets"))

from template import (
    DARK, TEXT, MUTED, LIGHT_LINE,
    PAGE_W, PAGE_H, CONTENT_WIDTH,
    CONTENT_MARGIN_L, CONTENT_MARGIN_R, CONTENT_MARGIN_T, CONTENT_MARGIN_B,
    build_styles, draw_border_and_page_number,
)


# ============ OUTPUT DIRECTORY & AUTO-NUMBERING ============

OUTPUT_DIR = Path.home() / "invoice-generator-output"


def parse_service_period_month(config) -> tuple:
    """
    Extract (year, month) from the invoice's service_period or date field.

    Tries service_period first (e.g., "March 2 - 27, 2026"), then falls back
    to invoice.date (e.g., "April 7, 2026"), then to today's date.
    Returns (year, month) as integers.

    Supports:
      - Month names: "March 2 - 27, 2026"
      - ISO: "2026-03-02"
      - European: "02.03.2026"
      - Slash: "03/02/2026" or "3/2/2026"
    """
    MONTH_MAP = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }
    candidates = [
        config.get("invoice", {}).get("service_period", ""),
        config.get("invoice", {}).get("date", ""),
    ]
    for text in candidates:
        if not text:
            continue
        text_lower = text.lower()

        # Try month names first (e.g., "March 2 - 27, 2026")
        for name, num in MONTH_MAP.items():
            if name in text_lower:
                year_match = re.search(r"\b(20\d{2})\b", text)
                if year_match:
                    return int(year_match.group(1)), num

        # Try ISO format: YYYY-MM-DD
        iso = re.search(r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b", text)
        if iso:
            return int(iso.group(1)), int(iso.group(2))

        # Try European format: DD.MM.YYYY
        eur = re.search(r"\b(\d{1,2})\.(\d{1,2})\.(20\d{2})\b", text)
        if eur:
            return int(eur.group(3)), int(eur.group(2))

        # Try slash format: MM/DD/YYYY
        slash = re.search(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b", text)
        if slash:
            return int(slash.group(3)), int(slash.group(1))

    return date.today().year, date.today().month


DEFAULT_NUMBER_PREFIX = "BL"


def next_invoice_number(year: int = None, month: int = None,
                        prefix: str = None) -> str:
    """
    Generate the next invoice number in {PREFIX}-{YYYY}-{MM}-{NNN} format.

    Scans OUTPUT_DIR for existing invoices matching the given prefix/year/month
    and returns the next sequential number. Defaults to the current date
    if year/month are not provided. Prefix defaults to "BL".
    """
    today = date.today()
    y = year or today.year
    m = month or today.month
    pfx = prefix or DEFAULT_NUMBER_PREFIX
    full_prefix = f"{pfx}-{y:04d}-{m:02d}-"

    # Find all existing invoice files (PDF or JSON) for this prefix-year-month
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    escaped_pfx = re.escape(pfx)
    pattern = re.compile(
        rf"^invoice-{escaped_pfx}-{y:04d}-{m:02d}-(\d{{3,}})\.(pdf|json)$",
        re.IGNORECASE,
    )
    max_count = 0
    for f in OUTPUT_DIR.iterdir():
        match = pattern.match(f.name)
        if match:
            max_count = max(max_count, int(match.group(1)))

    return f"{full_prefix}{max_count + 1:03d}"


def output_path_for(invoice_number: str) -> Path:
    """Return the canonical output path for a given invoice number."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR / f"invoice-{invoice_number}.pdf"


# ============ HELPERS ============

def thousand_sep_for(currency: str) -> str:
    """Return the conventional thousand separator for a currency."""
    # Swiss convention uses apostrophe; most others use comma
    if currency.upper() in ("CHF",):
        return "'"
    return ","


def fmt_money(amount, thousand_sep="'"):
    """Format a Decimal as '1'234.56' with configurable thousand separator."""
    s = f"{amount:,.2f}"
    return s.replace(",", thousand_sep)


def to_decimal(value):
    """Accept int/float/string and return Decimal for money math."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def list_invoices():
    """Scan the output folder for saved config JSONs and print a summary table."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_files = sorted(OUTPUT_DIR.glob("invoice-*.json"))
    if not json_files:
        print("No invoices found in", OUTPUT_DIR)
        return

    rows = []
    for jf in json_files:
        try:
            cfg = json.loads(jf.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        number = cfg.get("invoice", {}).get("number", "?")
        inv_date = cfg.get("invoice", {}).get("date", "?")
        recipient = cfg.get("recipient", {}).get("name", "?")
        currency = cfg.get("currency", "CHF")
        tsep = thousand_sep_for(currency)
        # Recompute gross from saved config
        try:
            totals = compute_totals(cfg)
            gross = f"{currency} {fmt_money(totals['gross'], tsep)}"
        except Exception:
            gross = "?"
        has_pdf = jf.with_suffix(".pdf").exists()
        rows.append((number, inv_date, recipient, gross, "yes" if has_pdf else "NO"))

    # Print table
    header = ("NUMBER", "DATE", "RECIPIENT", "GROSS", "PDF")
    widths = [max(len(header[i]), *(len(r[i]) for r in rows)) for i in range(5)]
    fmt_row = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt_row.format(*header))
    print(fmt_row.format(*("-" * w for w in widths)))
    for row in rows:
        print(fmt_row.format(*row))


MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _detect_csv_dialect(raw: str) -> tuple:
    """
    Auto-detect CSV delimiter and decimal separator.

    Returns (delimiter, decimal_char). Handles:
      - Semicolon-delimited with comma decimals (European: "3,50")
      - Comma-delimited with dot decimals (US/UK: "3.50")
      - Tab-delimited
    """
    # Count candidate delimiters in first 5 lines
    lines = raw.strip().split("\n")[:5]
    sample = "\n".join(lines)
    semicolons = sample.count(";")
    commas = sample.count(",")
    tabs = sample.count("\t")

    if tabs > semicolons and tabs > commas:
        return "\t", "."
    if semicolons > commas:
        return ";", ","   # European style
    return ",", "."       # US/UK style


def _parse_number(s: str, decimal_char: str) -> float:
    """Parse a number string with the given decimal character."""
    s = s.strip()
    if not s:
        raise ValueError("empty")
    if decimal_char == ",":
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")
    return float(s)


def _parse_date_cell(date_str: str) -> tuple:
    """
    Parse a date cell into (year, month, day, formatted_string).

    Supports:
      - DD.MM.YYYY (European)
      - YYYY-MM-DD (ISO)
      - MM/DD/YYYY (US)
      - "March 5, 2026" (English month name)
    Returns None if unparseable.
    """
    MONTH_MAP = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }
    date_str = date_str.strip()
    if not date_str:
        return None

    # DD.MM.YYYY
    m = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", date_str)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return y, mo, d, f"{MONTH_NAMES[mo]} {d}, {y}"

    # YYYY-MM-DD
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", date_str)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return y, mo, d, f"{MONTH_NAMES[mo]} {d}, {y}"

    # MM/DD/YYYY
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
    if m:
        mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return y, mo, d, f"{MONTH_NAMES[mo]} {d}, {y}"

    # English month name: "March 5, 2026" or "5 March 2026"
    for name, num in MONTH_MAP.items():
        if name in date_str.lower():
            year_match = re.search(r"\b(20\d{2})\b", date_str)
            day_match = re.search(r"\b(\d{1,2})\b", date_str)
            if year_match and day_match:
                y = int(year_match.group(1))
                d = int(day_match.group(1))
                return y, num, d, f"{MONTH_NAMES[num]} {d}, {y}"

    # Unparseable — return as-is with no structured date
    return None


def _detect_columns(header_row: list, delimiter: str) -> dict:
    """
    Detect which column indices hold date, hours, and description.

    Uses header labels if present, otherwise falls back to positional heuristics.
    Returns dict with keys: date_col, hours_col, desc_col, skip_cols.
    """
    mapping = {"date_col": None, "hours_col": None, "desc_col": None}
    header_lower = [c.strip().lower() for c in header_row]

    date_keywords = {"date", "datum", "tag"}
    hours_keywords = {"hours", "hrs", "hrs.", "time", "time (hrs.)", "zeit", "stunden"}
    desc_keywords = {"description", "desc", "beschreibung", "task", "activity", "work"}

    for i, label in enumerate(header_lower):
        if label in date_keywords and mapping["date_col"] is None:
            mapping["date_col"] = i
        elif label in hours_keywords and mapping["hours_col"] is None:
            mapping["hours_col"] = i
        elif label in desc_keywords and mapping["desc_col"] is None:
            mapping["desc_col"] = i

    # Fallback: if header has a leading empty/week column, assume cols 1/2/3
    if mapping["date_col"] is None:
        # Look for a column that contains date-like content
        mapping["date_col"] = 1 if len(header_row) > 3 else 0
    if mapping["hours_col"] is None:
        mapping["hours_col"] = mapping["date_col"] + 1
    if mapping["desc_col"] is None:
        mapping["desc_col"] = mapping["hours_col"] + 1

    return mapping


def import_timesheet_csv(csv_path: Path) -> dict:
    """
    Parse a timesheet CSV and return structured data for the invoice config.

    Auto-detects:
      - Delimiter (semicolon, comma, tab)
      - Decimal format (comma or dot)
      - Column mapping (by header labels or positional fallback)
      - Date formats (DD.MM.YYYY, YYYY-MM-DD, MM/DD/YYYY, English names)

    Returns dict with keys: total_hours, rate, line_items, service_period.
    """
    import csv
    from io import StringIO

    raw = csv_path.read_text(encoding="utf-8-sig")
    delimiter, decimal_char = _detect_csv_dialect(raw)

    reader = csv.reader(StringIO(raw), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        return {"total_hours": 0, "rate": None, "line_items": [], "service_period": None}

    header = rows[0]

    # Extract summary fields from header row (total time, rate)
    total_hours = None
    rate = None
    for i, cell in enumerate(header):
        cell_lower = cell.strip().lower()
        if cell_lower in ("total time", "total hours", "gesamtzeit") and i + 1 < len(header):
            try:
                total_hours = _parse_number(header[i + 1], decimal_char)
            except (ValueError, IndexError):
                pass
        if cell_lower in ("rate", "stundensatz", "hourly rate") and i + 1 < len(header):
            try:
                rate = _parse_number(header[i + 1], decimal_char)
            except (ValueError, IndexError):
                pass

    # Also check row 1 for summary fields (some CSVs put them on a second header line)
    if len(rows) > 1 and (total_hours is None or rate is None):
        for i, cell in enumerate(rows[1] if len(rows) > 1 else []):
            cell_lower = cell.strip().lower()
            if cell_lower in ("total time", "total hours") and i + 1 < len(rows[1]):
                try:
                    total_hours = total_hours or _parse_number(rows[1][i + 1], decimal_char)
                except (ValueError, IndexError):
                    pass
            if cell_lower in ("rate", "hourly rate") and i + 1 < len(rows[1]):
                try:
                    rate = rate or _parse_number(rows[1][i + 1], decimal_char)
                except (ValueError, IndexError):
                    pass

    # Detect columns
    col_map = _detect_columns(header, delimiter)
    date_col = col_map["date_col"]
    hours_col = col_map["hours_col"]
    desc_col = col_map["desc_col"]

    # Parse data rows
    line_items = []
    dates_seen = []
    for row in rows[1:]:
        if len(row) <= max(date_col, hours_col, desc_col):
            continue

        date_str = row[date_col].strip()
        hours_str = row[hours_col].strip()
        desc = row[desc_col].strip()

        if not desc:
            continue

        # Parse date
        parsed_date = _parse_date_cell(date_str)
        if parsed_date:
            y, mo, d, formatted_date = parsed_date
            dates_seen.append((y, mo, d))
        else:
            formatted_date = date_str if date_str else ""

        # Parse hours
        hours = None
        if hours_str:
            try:
                hours = _parse_number(hours_str, decimal_char)
            except ValueError:
                pass

        item = {"date": formatted_date, "description": desc}
        if hours is not None:
            item["hours"] = hours
        line_items.append(item)

    # Derive service_period from first and last dates
    service_period = None
    if dates_seen:
        dates_seen.sort()
        first = dates_seen[0]
        last = dates_seen[-1]
        if first[1] == last[1] and first[0] == last[0]:
            service_period = f"{MONTH_NAMES[first[1]]} {first[2]} - {last[2]}, {first[0]}"
        else:
            service_period = (
                f"{MONTH_NAMES[first[1]]} {first[2]}, {first[0]} - "
                f"{MONTH_NAMES[last[1]]} {last[2]}, {last[0]}"
            )

    # Compute total hours from line items if not in header
    if total_hours is None:
        total_hours = sum(item.get("hours", 0) for item in line_items)

    return {
        "total_hours": total_hours,
        "rate": rate,
        "line_items": line_items,
        "service_period": service_period,
    }


def validate_config(config):
    """Validate required config fields and raise clear errors for missing ones."""
    errors = []

    # Required top-level objects
    for key in ("supplier", "recipient", "invoice", "service"):
        if key not in config:
            errors.append(f"Missing required section: '{key}'")

    # Supplier fields
    supplier = config.get("supplier", {})
    if not supplier.get("name"):
        errors.append("Missing supplier.name")
    if not supplier.get("address"):
        errors.append("Missing supplier.address")

    # Recipient fields
    recipient = config.get("recipient", {})
    if not recipient.get("name"):
        errors.append("Missing recipient.name")
    if not recipient.get("address"):
        errors.append("Missing recipient.address")

    # Invoice metadata
    invoice = config.get("invoice", {})
    if not invoice.get("number"):
        errors.append("Missing invoice.number")
    if not invoice.get("date"):
        errors.append("Missing invoice.date")

    # Service
    service = config.get("service", {})
    if not service.get("description"):
        errors.append("Missing service.description")

    # Amount: need (hours + rate) or total
    has_hours = config.get("hours") is not None and config.get("rate") is not None
    has_total = config.get("total") is not None
    if not has_hours and not has_total:
        errors.append("Must provide either (hours + rate) or total")

    # VAT: if mode is inclusive/exclusive, rate is required
    vat = config.get("vat", {})
    if vat.get("mode") in ("inclusive", "exclusive") and vat.get("rate") is None:
        errors.append(f"VAT mode is '{vat['mode']}' but vat.rate is missing")

    if errors:
        raise ValueError("Config validation failed:\n  - " + "\n  - ".join(errors))


def compute_totals(config):
    """
    Compute net, VAT, and gross based on config.

    VAT handling modes (config["vat"]["mode"]):
      - "inclusive": rate is tax-inclusive, extract VAT from gross
      - "exclusive": rate is tax-exclusive, add VAT on top
      - "none": no VAT line (e.g., reverse charge, non-VAT supplier)

    The rate can come from:
      - hours * rate (if both provided)
      - flat "total" (if hours/rate not provided)
    """
    hours = config.get("hours")
    rate = config.get("rate")
    flat_total = config.get("total")

    if hours is not None and rate is not None:
        hours_d = to_decimal(hours)
        rate_d = to_decimal(rate)
        line_total = (hours_d * rate_d).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    elif flat_total is not None:
        hours_d = None
        rate_d = None
        line_total = to_decimal(flat_total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        raise ValueError("Config must provide either (hours + rate) or total")

    vat_cfg = config.get("vat", {"mode": "none"})
    vat_mode = vat_cfg.get("mode", "none")
    vat_rate = to_decimal(vat_cfg.get("rate", "0"))  # e.g., 0.081 for 8.1%

    if vat_mode == "inclusive":
        # line_total already contains VAT - extract it
        gross = line_total
        net = (gross / (Decimal("1") + vat_rate)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)
        vat_amount = (gross - net).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)
    elif vat_mode == "exclusive":
        net = line_total
        vat_amount = (net * vat_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)
        gross = net + vat_amount
    elif vat_mode == "none":
        net = line_total
        vat_amount = Decimal("0.00")
        gross = line_total
    else:
        raise ValueError(f"Invalid vat mode: {vat_mode!r}. Use inclusive|exclusive|none")

    return {
        "hours": hours_d,
        "rate": rate_d,
        "net": net,
        "vat_amount": vat_amount,
        "vat_rate": vat_rate,
        "vat_mode": vat_mode,
        "gross": gross,
        "line_total": line_total,  # what shows in the services table row
    }


# ============ STORY BUILDERS ============

def build_story(config, totals, styles, currency):
    """Build the ReportLab flowables list for the invoice + optional appendix."""
    story = []
    tsep = thousand_sep_for(currency)
    supplier = config["supplier"]
    recipient = config["recipient"]
    meta = config["invoice"]

    # === HEADER: INVOICE/CREDIT NOTE label + wordmark | dark pill ===
    is_credit = totals["gross"] < 0
    doc_label = "CREDIT NOTE" if is_credit else "INVOICE"
    left_head = Table([
        [Paragraph(doc_label, styles["invoice_label"])],
        [Paragraph(f"{supplier['name']}.", styles["wordmark"])],
    ], colWidths=[110 * mm])
    left_head.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    pill = Table([
        [Paragraph(
            f"<font color='white'><b>NO. {meta['number']}</b></font>",
            styles["pill"])],
        [Paragraph(
            f"<font color='white'><b>{meta['date']}</b></font>",
            styles["pill"])],
    ], colWidths=[44 * mm])
    pill.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (0, 0), (0, 0), 2),
        ("TOPPADDING", (0, 1), (0, 1), 0),
        ("BOTTOMPADDING", (0, 1), (0, 1), 10),
    ]))

    header = Table([[left_head, pill]],
                   colWidths=[110 * mm, CONTENT_WIDTH - 110 * mm])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header)
    story.append(Spacer(1, 4 * mm))

    # === SUPPLIER BLOCK (left) + META (right) ===
    # Note: supplier name is already shown as the wordmark in the header,
    # so we only render address + VAT here to avoid duplication.
    supplier_lines = list(supplier["address"])
    if supplier.get("vat"):
        supplier_lines.append(f"VAT: {supplier['vat']}")
    supplier_html = "<br/>".join(supplier_lines)

    meta_rows = [
        f"<font color='#6b7280'>Invoice date:</font> {meta['date']}",
    ]
    if meta.get("service_period"):
        meta_rows.append(
            f"<font color='#6b7280'>Service period:</font> {meta['service_period']}")
    if meta.get("due_date"):
        meta_rows.append(
            f"<font color='#6b7280'>Due date:</font> {meta['due_date']}")
    meta_html = "<br/>".join(meta_rows)

    top = Table([[
        Paragraph(supplier_html, styles["body"]),
        Paragraph(meta_html, styles["body_right"]),
    ]], colWidths=[90 * mm, CONTENT_WIDTH - 90 * mm])
    top.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(top)
    story.append(Spacer(1, 8 * mm))

    # === BILL TO ===
    bill_lines = [
        "<font color='#6b7280'>BILL TO:</font>",
        "",  # blank line
        f"<b>{recipient['name'].upper()}</b>",
    ]
    bill_lines.extend(recipient["address"])
    bill_html = "<br/>".join(bill_lines)
    story.append(Paragraph(bill_html, styles["body"]))
    story.append(Spacer(1, 8 * mm))

    # Top rule
    rule = Table([[""]], colWidths=[CONTENT_WIDTH], rowHeights=[0.1])
    rule.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.75, LIGHT_LINE),
    ]))
    story.append(rule)
    story.append(Spacer(1, 4 * mm))

    # === SERVICES TABLE ===
    # Services row description can include a subtitle via service.subtitle
    service = config["service"]
    desc_html = service["description"]
    if service.get("subtitle"):
        desc_html += f"<br/><font size=8 color='#6b7280'>{service['subtitle']}</font>"
    if config.get("line_items"):
        desc_html += "<br/><font size=8 color='#6b7280'>See Appendix for itemised breakdown</font>"

    has_hours = totals["hours"] is not None
    if has_hours:
        services_data = [
            [
                Paragraph("DESCRIPTION", styles["th"]),
                Paragraph("HOURS", styles["th_right"]),
                Paragraph("RATE", styles["th_right"]),
                Paragraph("TOTAL", styles["th_right"]),
            ],
            [
                Paragraph(desc_html, styles["td"]),
                Paragraph(f"{totals['hours']:.1f}", styles["td_right"]),
                Paragraph(f"{currency} {fmt_money(totals['rate'], tsep)}", styles["td_right"]),
                Paragraph(f"{currency} {fmt_money(totals['line_total'], tsep)}", styles["td_right"]),
            ],
        ]
        services_table = Table(services_data,
            colWidths=[90 * mm, 22 * mm, 25 * mm, CONTENT_WIDTH - 137 * mm])
    else:
        services_data = [
            [
                Paragraph("DESCRIPTION", styles["th"]),
                Paragraph("TOTAL", styles["th_right"]),
            ],
            [
                Paragraph(desc_html, styles["td"]),
                Paragraph(f"{currency} {fmt_money(totals['line_total'], tsep)}", styles["td_right"]),
            ],
        ]
        services_table = Table(services_data,
            colWidths=[CONTENT_WIDTH - 40 * mm, 40 * mm])

    services_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, LIGHT_LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, 0), 4),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 1), (-1, 1), 10),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
    ]))
    story.append(services_table)
    story.append(Spacer(1, 6 * mm))

    # === TOTALS STACK (right-aligned) ===
    tot_rows = [
        [Paragraph("SUB TOTAL", styles["tot_label"]),
         Paragraph(f"{currency} {fmt_money(totals['net'], tsep)}", styles["tot_value"])],
    ]
    if totals["vat_mode"] != "none":
        vat_pct = (totals["vat_rate"] * 100).quantize(Decimal("0.1"))
        # Strip trailing .0 for clean display (8.0 -> 8, 8.1 -> 8.1)
        vat_pct_str = str(vat_pct).rstrip("0").rstrip(".") if "." in str(vat_pct) else str(vat_pct)
        tot_rows.append([
            Paragraph(f"VAT ({vat_pct_str}%)", styles["tot_label"]),
            Paragraph(f"{currency} {fmt_money(totals['vat_amount'], tsep)}", styles["tot_value"]),
        ])
    tot_rows.append([
        Paragraph("TOTAL AMOUNT", styles["tot_label_bold"]),
        Paragraph(f"{currency} {fmt_money(totals['gross'], tsep)}", styles["tot_value_bold"]),
    ])
    amount_paid = to_decimal(config.get("amount_paid", "0"))
    tot_rows.append([
        Paragraph("AMOUNT PAID", styles["tot_label"]),
        Paragraph(f"{currency} {fmt_money(amount_paid, tsep)}", styles["tot_value"]),
    ])

    tot_inner = Table(tot_rows, colWidths=[42 * mm, 38 * mm])
    tot_inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    tot_wrap = Table([[None, tot_inner]],
        colWidths=[CONTENT_WIDTH - 80 * mm, 80 * mm])
    tot_wrap.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(tot_wrap)
    story.append(Spacer(1, 2 * mm))

    # Separator above balance
    sep = Table([[None, ""]],
        colWidths=[CONTENT_WIDTH - 80 * mm, 80 * mm], rowHeights=[0.1])
    sep.setStyle(TableStyle([("LINEABOVE", (1, 0), (1, 0), 0.75, DARK)]))
    story.append(sep)
    story.append(Spacer(1, 3 * mm))

    # Balance Due
    balance_due = totals["gross"] - amount_paid
    bal_inner = Table([[
        Paragraph("BALANCE DUE", styles["balance"]),
        Paragraph(f"{currency} {fmt_money(balance_due, tsep)}", styles["balance"]),
    ]], colWidths=[42 * mm, 38 * mm])
    bal_inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    bal_wrap = Table([[None, bal_inner]],
        colWidths=[CONTENT_WIDTH - 80 * mm, 80 * mm])
    bal_wrap.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(bal_wrap)
    story.append(Spacer(1, 10 * mm))

    # Bottom rule
    rule2 = Table([[""]], colWidths=[CONTENT_WIDTH], rowHeights=[0.1])
    rule2.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.75, LIGHT_LINE),
    ]))
    story.append(rule2)
    story.append(Spacer(1, 5 * mm))

    # === FOOTER: Notes box (left, optional) | Payment Info (right) ===
    payment = config.get("payment", {})
    pay_lines = ["<b>PAYMENT INFORMATION</b>", ""]
    if payment.get("account_holder"):
        pay_lines.append(f"Account holder: {payment['account_holder']}")
    if payment.get("iban"):
        pay_lines.append(f"IBAN: {payment['iban']}")
    if payment.get("bic"):
        pay_lines.append(f"BIC/SWIFT: {payment['bic']}")
    pay_lines.append(f"Payment reference: {meta['number']}")
    pay_html = "<br/>".join(pay_lines)

    notes = config.get("notes", "")  # left box - empty if not provided
    notes_html = notes if notes else ""

    footer = Table([[
        Paragraph(notes_html, styles["body"]),
        Paragraph(pay_html, styles["body"]),
    ]], colWidths=[(CONTENT_WIDTH - 6 * mm) / 2, (CONTENT_WIDTH - 6 * mm) / 2])
    footer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 3 * mm),
        ("LEFTPADDING", (1, 0), (1, 0), 3 * mm),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("LINEBEFORE", (1, 0), (1, 0), 0.5, LIGHT_LINE),
    ]))
    story.append(footer)

    # === APPENDIX (optional) ===
    line_items = config.get("line_items") or []
    if line_items:
        story.append(PageBreak())
        story.append(Paragraph("APPENDIX", styles["app_label"]))
        appendix_title = config.get("appendix_title", "Work Breakdown.")
        story.append(Paragraph(appendix_title, styles["app_title"]))
        story.append(Spacer(1, 3 * mm))

        subtitle_parts = []
        if has_hours:
            subtitle_parts.append(f"Detailed breakdown of {totals['hours']:.1f} hours")
        else:
            subtitle_parts.append("Detailed breakdown of work performed")
        if meta.get("service_period"):
            subtitle_parts.append(f"during {meta['service_period']}")
        if config.get("appendix_subtitle_suffix"):
            subtitle_parts.append(config["appendix_subtitle_suffix"])
        story.append(Paragraph(" ".join(subtitle_parts) + ".", styles["body"]))
        story.append(Spacer(1, 6 * mm))

        # Appendix table: Date | Hours | Description
        # Hours column only shown if any item has hours
        any_hours = any(item.get("hours") is not None for item in line_items)

        if any_hours:
            app_data = [[
                Paragraph("DATE", styles["th"]),
                Paragraph("HOURS", styles["th_right"]),
                Paragraph("DESCRIPTION", styles["th"]),
            ]]
            for item in line_items:
                app_data.append([
                    Paragraph(item.get("date", ""), styles["td"]),
                    Paragraph(f"{float(item.get('hours', 0)):.1f}" if item.get("hours") is not None else "",
                              styles["td_right"]),
                    Paragraph(item.get("description", ""), styles["td_wrap"]),
                ])
            # Total row
            total_hours = sum(to_decimal(item.get("hours", 0)) for item in line_items)
            app_data.append([
                Paragraph("", styles["td"]),
                Paragraph(f"<b>{total_hours:.1f}</b>",
                          ParagraphStyle_copy(styles["td_right"], bold=True, size=10)),
                Paragraph("<b>TOTAL HOURS</b>",
                          ParagraphStyle_copy(styles["td"], bold=True, size=10)),
            ])
            col_widths = [30 * mm, 22 * mm, CONTENT_WIDTH - 52 * mm]
            style_cmds = [
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, LIGHT_LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (1, 0), (1, -1), 6),
                ("LEFTPADDING", (2, 0), (2, -1), 6),
                ("RIGHTPADDING", (2, 0), (2, -1), 0),
                ("TOPPADDING", (0, 0), (-1, 0), 4),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
                ("LINEABOVE", (0, -1), (-1, -1), 0.75, DARK),
                ("TOPPADDING", (0, -1), (-1, -1), 8),
            ]
        else:
            app_data = [[
                Paragraph("DATE", styles["th"]),
                Paragraph("DESCRIPTION", styles["th"]),
            ]]
            for item in line_items:
                app_data.append([
                    Paragraph(item.get("date", ""), styles["td"]),
                    Paragraph(item.get("description", ""), styles["td_wrap"]),
                ])
            col_widths = [30 * mm, CONTENT_WIDTH - 30 * mm]
            style_cmds = [
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, LIGHT_LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (1, 0), (1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, 0), 4),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            ]

        app_table = Table(app_data, colWidths=col_widths, repeatRows=1)
        app_table.setStyle(TableStyle(style_cmds))
        story.append(app_table)

    return story


def ParagraphStyle_copy(base, bold=False, size=None):
    """Derive a variant style from an existing one for inline reuse."""
    from reportlab.lib.styles import ParagraphStyle as PS
    return PS(
        f"{base.name}_var",
        parent=base,
        fontName="Helvetica-Bold" if bold else base.fontName,
        fontSize=size if size else base.fontSize,
    )


# ============ MAIN ============

def generate(config, output_path):
    """Two-pass build: first pass counts pages, second pass draws correct N/total."""
    validate_config(config)
    totals = compute_totals(config)
    currency = config.get("currency", "CHF")
    styles = build_styles()

    # --- Pass 1: dry build to count pages ---
    story1 = build_story(config, totals, styles, currency)
    dummy_path = str(Path(output_path).with_suffix(".__tmp__.pdf"))
    doc1 = SimpleDocTemplate(
        dummy_path, pagesize=A4,
        leftMargin=CONTENT_MARGIN_L, rightMargin=CONTENT_MARGIN_R,
        topMargin=CONTENT_MARGIN_T, bottomMargin=CONTENT_MARGIN_B,
    )
    doc1.build(story1)  # no page decoration yet
    total_pages = doc1.page

    # --- Pass 2: real build with page numbers ---
    styles2 = build_styles()
    story2 = build_story(config, totals, styles2, currency)
    doc2 = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=CONTENT_MARGIN_L, rightMargin=CONTENT_MARGIN_R,
        topMargin=CONTENT_MARGIN_T, bottomMargin=CONTENT_MARGIN_B,
        title=f"Invoice {config['invoice']['number']}",
        author=config["supplier"]["name"],
    )

    def on_page(canvas, doc):
        draw_border_and_page_number(canvas, doc, total_pages)

    doc2.build(story2, onFirstPage=on_page, onLaterPages=on_page)

    # Clean up dry-run output
    Path(dummy_path).unlink(missing_ok=True)

    # Save a copy of the config JSON alongside the PDF for audit/regeneration
    config_path = Path(output_path).with_suffix(".json")
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    return {
        "output": str(output_path),
        "config": str(config_path),
        "invoice_number": config["invoice"]["number"],
        "pages": total_pages,
        "net": str(totals["net"]),
        "vat": str(totals["vat_amount"]),
        "gross": str(totals["gross"]),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate a PDF invoice using the Modern Black template."
    )
    parser.add_argument("--config", required=False, default=None,
                        help="Path to JSON config file")
    parser.add_argument("--output", required=False, default=None,
                        help="Path to output PDF file (auto-generated if omitted)")
    parser.add_argument("--auto-number", action="store_true",
                        help="Auto-generate the invoice number (BL-YYYY-MM-NNN)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview totals without generating a PDF")
    parser.add_argument("--list", action="store_true",
                        help="List all generated invoices from the output folder")
    parser.add_argument("--import-csv", default=None,
                        help="Path to a timesheet CSV to auto-populate line_items, hours, and service_period")
    parser.add_argument("--regenerate", default=None,
                        help="Path to a saved invoice JSON (from output folder) to re-render as PDF")
    args = parser.parse_args()

    # --list mode: scan output folder and print summary
    if args.list:
        list_invoices()
        sys.exit(0)

    # --regenerate mode: load saved JSON as the config
    if args.regenerate:
        regen_path = Path(args.regenerate)
        if not regen_path.exists():
            parser.error(f"File not found: {regen_path}")
        config = json.loads(regen_path.read_text())
        out = args.output if args.output else str(regen_path.with_suffix(".pdf"))
        result = generate(config, out)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    if not args.config:
        parser.error("--config is required unless using --list or --regenerate")

    config = json.loads(Path(args.config).read_text())

    # --import-csv: parse timesheet and merge into config
    if args.import_csv:
        csv_data = import_timesheet_csv(Path(args.import_csv))
        config.setdefault("hours", csv_data["total_hours"])
        config.setdefault("line_items", csv_data["line_items"])
        if csv_data.get("rate") and "rate" not in config:
            config["rate"] = csv_data["rate"]
        if csv_data.get("service_period"):
            config.setdefault("invoice", {}).setdefault(
                "service_period", csv_data["service_period"])

    # Auto-generate invoice number if requested
    if args.auto_number:
        year, month = parse_service_period_month(config)
        pfx = config.get("number_prefix", DEFAULT_NUMBER_PREFIX)
        inv_number = next_invoice_number(year, month, prefix=pfx)
        config["invoice"]["number"] = inv_number

    # Dry-run: compute and print totals, then exit
    if args.dry_run:
        totals = compute_totals(config)
        currency = config.get("currency", "CHF")
        tsep = thousand_sep_for(currency)
        amount_paid = to_decimal(config.get("amount_paid", "0"))
        balance_due = totals["gross"] - amount_paid
        preview = {
            "invoice_number": config["invoice"]["number"],
            "currency": currency,
            "hours": str(totals["hours"]) if totals["hours"] else None,
            "rate": str(totals["rate"]) if totals["rate"] else None,
            "net": f"{currency} {fmt_money(totals['net'], tsep)}",
            "vat": f"{currency} {fmt_money(totals['vat_amount'], tsep)}" if totals["vat_mode"] != "none" else "N/A",
            "vat_mode": totals["vat_mode"],
            "gross": f"{currency} {fmt_money(totals['gross'], tsep)}",
            "amount_paid": f"{currency} {fmt_money(amount_paid, tsep)}",
            "balance_due": f"{currency} {fmt_money(balance_due, tsep)}",
        }
        print(json.dumps(preview, indent=2))
        sys.exit(0)

    # Default output path: ~/invoice-generator-output/invoice-{number}.pdf
    inv_number = config["invoice"]["number"]
    out = args.output if args.output else str(output_path_for(inv_number))

    result = generate(config, out)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
