#!/usr/bin/env python3
"""
Convert a Markdown file to a plain black-and-white PDF using fpdf2.
Uses system Arial TTF fonts for full Unicode support.
Simple formatting: bold headings, italic quotes, bullet lists. No colours or effects.
"""

import argparse
import os
import re
import sys

try:
    from fpdf import FPDF
except ImportError:
    print("ERROR: fpdf2 not installed. Run: pip install fpdf2 --break-system-packages", file=sys.stderr)
    sys.exit(1)

# macOS system font paths for Arial (Unicode-capable)
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_ITALIC = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"
FONT_BOLD_ITALIC = "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf"
FONT_FAMILY = "Arial"


class MarkdownPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font(FONT_FAMILY, "", FONT_REGULAR)
        self.add_font(FONT_FAMILY, "B", FONT_BOLD)
        self.add_font(FONT_FAMILY, "I", FONT_ITALIC)
        self.add_font(FONT_FAMILY, "BI", FONT_BOLD_ITALIC)
        self.add_page()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)
        self.set_font(FONT_FAMILY, size=10)

    def add_heading(self, text, level=1):
        sizes = {1: 18, 2: 14, 3: 12}
        size = sizes.get(level, 10)
        self.ln(4 if level == 1 else 3)
        self.set_font(FONT_FAMILY, "B", size)
        self.multi_cell(w=0, h=size * 0.6, text=text)
        self.ln(2)
        if level == 1:
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(3)
        self.set_font(FONT_FAMILY, size=10)

    def add_paragraph(self, text):
        self.set_font(FONT_FAMILY, size=10)
        self.multi_cell(w=0, h=5, text=text, markdown=True)
        self.ln(3)

    def add_blockquote(self, text):
        self.set_x(self.l_margin + 10)
        self.set_font(FONT_FAMILY, "I", 10)
        self.multi_cell(w=self.w - self.l_margin - 10 - self.r_margin, h=5, text=text)
        self.set_font(FONT_FAMILY, size=10)
        self.ln(3)

    def add_bullet(self, text):
        x = self.l_margin + 5
        self.set_x(x)
        self.cell(w=5, h=5, text="\u2022")
        self.multi_cell(w=self.w - x - 5 - self.r_margin, h=5, text=text, markdown=True)
        self.ln(1)

    def add_meta(self, text):
        self.set_font(FONT_FAMILY, size=9)
        self.multi_cell(w=0, h=5, text=text)
        self.set_font(FONT_FAMILY, size=10)
        self.ln(1)


def parse_and_render(md_text, pdf):
    lines = md_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]

        # Headings
        heading_match = re.match(r'^(#{1,3})\s+(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            pdf.add_heading(heading_match.group(2), level)
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^---+\s*$', line):
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(3)
            i += 1
            continue

        # Blockquotes (collect multi-line)
        if line.startswith('>'):
            quote_lines = []
            while i < len(lines) and lines[i].startswith('>'):
                quote_lines.append(lines[i].lstrip('> '))
                i += 1
            pdf.add_blockquote(' '.join(quote_lines))
            continue

        # Bullet lists
        if re.match(r'^[-*]\s+', line):
            pdf.add_bullet(re.sub(r'^[-*]\s+', '', line))
            i += 1
            continue

        # Meta lines (bold label: value)
        meta_match = re.match(r'^\*\*(.+?):\*\*\s*(.+)', line)
        if meta_match:
            pdf.add_meta(f"{meta_match.group(1)}: {meta_match.group(2)}")
            i += 1
            continue

        # Italic note lines
        if re.match(r'^\*[^*]+\*$', line):
            pdf.add_meta(line.strip('*'))
            i += 1
            continue

        # Empty lines
        if not line.strip():
            i += 1
            continue

        # Regular paragraph (collect consecutive non-empty lines)
        para_lines = []
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,3}\s|[-*]\s|>|---|\*\*\w+:\*\*|\*[^*]+\*$)', lines[i]):
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            pdf.add_paragraph(' '.join(para_lines))
            continue

        i += 1


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF")
    parser.add_argument("input_file", help="Path to the Markdown file")
    parser.add_argument("--output", help="Output PDF path (default: same name with .pdf extension)")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"ERROR: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.input_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    output_path = args.output or args.input_file.rsplit('.', 1)[0] + '.pdf'

    pdf = MarkdownPDF()
    parse_and_render(md_text, pdf)
    pdf.output(output_path)
    print(f"PDF saved: {output_path}")


if __name__ == "__main__":
    main()
