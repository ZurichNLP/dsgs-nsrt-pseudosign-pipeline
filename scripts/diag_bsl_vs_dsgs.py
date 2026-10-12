"""
Diagnostic: List all signs where BSL 4 says complex but DSGS 6 says simple.
Expected: all such signs have base handshape ∈ {C (E00A), O (E007)}.

Input:  output/classified_details.csv
Output: output/bsl_vs_dsgs_diff.csv
"""

import csv
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / 'output'

INPUT_FILE = OUTPUT_DIR / 'analysis_ready_pool.csv'
OUTPUT_FILE = OUTPUT_DIR / 'bsl_vs_dsgs_diff.csv'


def main():
    with open(INPUT_FILE, encoding='utf-8') as f:
        diff_rows = [
            r for r in csv.DictReader(f)
            if r['handshape_bsl'] == 'complex' and r['handshape_dsgs'] == 'simple'
        ]

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=[
            'gloss_id', 'corpus_freq', 'base_handshape_cp',
            'handshape_bsl', 'handshape_dsgs',
            'handedness', 'hamnosys_length'
        ])
        w.writeheader()
        for r in diff_rows:
            w.writerow({k: r[k] for k in w.fieldnames})

    print(f"Total signs BSL=complex, DSGS=simple: {len(diff_rows)}")
    print(f"Written to: {OUTPUT_FILE}\n")

    # Breakdown by base handshape
    hs_dist = Counter(r['base_handshape_cp'] for r in diff_rows)
    print("Breakdown by base handshape (should be C or O only):")
    for cp, n in hs_dist.most_common():
        label = {'U+E007': 'O (pinchall)', 'U+E00A': 'C (ceeall)'}.get(cp, cp)
        print(f"  {cp}  ({label:20s}) count={n}")

    # First 10 examples
    print(f"\nFirst 15 examples:")
    for r in diff_rows[:15]:
        print(f"  {r['gloss_id']:25s} base={r['base_handshape_cp']}  "
              f"handedness={r['handedness']}")


if __name__ == '__main__':
    main()