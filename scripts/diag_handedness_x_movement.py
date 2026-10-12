"""
Diagnostic: Handedness × movement (3-way) cross-tabulation.
Shows whether different handedness classes have different movement distributions.

Input:  output/classified_details.csv
Output: output/handedness_x_movement.csv
"""

import csv
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / 'output'

INPUT_FILE = OUTPUT_DIR / 'analysis_ready_pool.csv'
OUTPUT_FILE = OUTPUT_DIR / 'handedness_x_movement.csv'


def main():
    counts = Counter()
    with open(INPUT_FILE, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            counts[(r['handedness'], r['movement_class'])] += 1

    handedness_vals = ['single', 'sym_two', 'asym_two']
    movement_vals = ['simple', 'complex']


    print("Handedness × Movement (3-way):")
    for h in ['single', 'sym_two', 'asym_two']:
        row_total = sum(counts[(h, m)] for m in ['static', 'simple', 'complex'])
        static_n = counts[(h, 'static')]
        simple_n = counts[(h, 'simple')]
        complex_n = counts[(h, 'complex')]
        cp = 100 * complex_n / row_total if row_total else 0
        print(f"  {h}: simple={simple_n}, complex={complex_n}, "
              f"total={row_total}, complex={cp:.1f}%")


    # Write CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['handedness', 'simple', 'complex',
                    'total', 'complex_pct'])
        for h in handedness_vals:
            row_total = sum(counts[(h, m)] for m in movement_vals)
            simple_n = counts[(h, 'simple')]
            complex_n = counts[(h, 'complex')]
            cp = 100 * complex_n / row_total if row_total else 0
            w.writerow([h, simple_n, complex_n, row_total, f'{cp:.1f}'])

    print(f"\nWritten to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()