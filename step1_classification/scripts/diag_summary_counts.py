"""
Diagnostic: Aggregate counts for the 2x2 tables (BSL/DSGS × strict/excluded).
Produces the summary tables.

Input:  output/classified_details.csv
Output: output/summary_counts.csv
"""

import csv
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent / 'output'

INPUT_FILE = OUTPUT_DIR / 'analysis_ready_pool.csv'
OUTPUT_FILE = OUTPUT_DIR / 'summary_counts.csv'


def main():
    with open(INPUT_FILE, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    variants = [
        ('BSL 4', 'handshape_bsl', 'movement_class'),
        ('DSGS 6', 'handshape_dsgs', 'movement_class'),
    ]

    all_output = []
    for hs_scheme, hs_field, mv_field in variants:
        # Count per cell
        counts = Counter()
        for r in rows:
            hs, mv = r[hs_field], r[mv_field]
            if hs and mv:
                counts[(hs, mv)] += 1

        total = sum(counts.values())
        row_totals = {
            hs: counts[(hs, 'simple')] + counts[(hs, 'complex')]
            for hs in ['simple', 'complex']
        }
        col_totals = {
            mv: counts[('simple', mv)] + counts[('complex', mv)]
            for mv in ['simple', 'complex']
        }

        for hs in ['simple', 'complex']:
            for mv in ['simple', 'complex']:
                n = counts[(hs, mv)]
                pct_of_total = 100 * n / total if total else 0
                pct_of_row = 100 * n / row_totals[hs] if row_totals[hs] else 0
                pct_of_col = 100 * n / col_totals[mv] if col_totals[mv] else 0
                all_output.append({
                    'handshape_scheme': hs_scheme,
                    'handshape_class': hs,
                    'movement_class': mv,
                    'count': n,
                    'row_total': row_totals[hs],
                    'col_total': col_totals[mv],
                    'grand_total': total,
                    'pct_of_total': f'{pct_of_total:.1f}',
                    'pct_of_row': f'{pct_of_row:.1f}',
                    'pct_of_col': f'{pct_of_col:.1f}',
                })

    # Write CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(all_output[0].keys()))
        w.writeheader()
        w.writerows(all_output)

    print(f"Written to: {OUTPUT_FILE}")
    print(f"Total rows: {len(all_output)}  (4 variants × 4 cells)\n")

   
    print("Summary (BSL 4):")
    print(f"{'':22s}  {'Simple mv':>10s}  {'Complex mv':>10s}  {'Row total':>10s}")
    for row in all_output[:4]:
        hs = row['handshape_class']
        mv = row['movement_class']
        n = row['count']
        rt = row['row_total']
        if mv == 'simple':
            _line = f"  {hs} handshape:  {n:>10}"
            print(_line, end='')
        else:
            print(f"  {n:>10}  {rt:>10}")


if __name__ == '__main__':
    main()