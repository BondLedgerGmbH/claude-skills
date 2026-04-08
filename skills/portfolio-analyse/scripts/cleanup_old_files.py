#!/usr/bin/env python3
"""Delete intermediate portfolio-analyse files older than a given age.

Usage:
    python3 cleanup_old_files.py <output_dir> [max_age_days]

Arguments:
    output_dir:    Path to the portfolio-analyse output directory
    max_age_days:  Delete files older than this (default: 7)
"""

import os
import glob
import sys
from datetime import datetime, timedelta

if len(sys.argv) < 2:
    print("Usage: python3 cleanup_old_files.py <output_dir> [max_age_days]")
    sys.exit(1)

output_dir = sys.argv[1]
max_age_days = int(sys.argv[2]) if len(sys.argv) > 2 else 7

cutoff = datetime.now() - timedelta(days=max_age_days)
deleted = []

patterns = [
    "0-portfolio-snapshots/portfolio-summary-*.json",
    "0-thesis-inputs/thesis-input-*.md",
    "1-market-research/market-research-cache-*.md",
    "2-opportunity-scoring/opportunity-scoring-*.md",
    "3-impact-analysis/impact-analysis-*.md",
    "3-hedge-data/hedge-data-*.json",
]

for pat in patterns:
    for f in sorted(glob.glob(os.path.join(output_dir, pat))):
        basename = os.path.basename(f)
        parts = basename.split("-")
        try:
            for i in range(len(parts)):
                if len(parts[i]) == 4 and parts[i].isdigit():
                    date_str = "-".join(parts[i : i + 3])
                    file_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    if file_date < cutoff:
                        os.remove(f)
                        deleted.append(basename)
                    break
        except (ValueError, IndexError):
            pass

print(f"Deleted {len(deleted)} old files (cutoff: {cutoff.strftime('%Y-%m-%d')})")
for d in deleted:
    print(f"  - {d}")
