"""
Step 2.5: Apply analytical filters. Based on Sarah's consultation.

Drop all static signs. Most are incomplete 
HamNoSys transcriptions (handshape symbols only, no movement notation); 
remainder is mostly fingerspelling (already excluded in Step 1). 
Neither fits Mann 2010's handshape × movement framework.

Input:  output/classified_details.csv
Output: output/analysis_ready_pool.csv
"""

import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent / 'output'

INPUT_FILE  = OUTPUT_DIR / 'classified_details.csv'
OUTPUT_FILE = OUTPUT_DIR / 'analysis_ready_pool.csv'


def main():
    with open(INPUT_FILE, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    kept = [r for r in rows if r['movement_class_3way'] != 'static']
    dropped = len(rows) - len(kept)

    final_fields = [
        'gloss_id', 'corpus_freq', 'hamnosys', 'hamnosys_length',
        'naming_style', 'handedness',
        'base_handshape_cp', 'handshape_bsl', 'handshape_dsgs',
        'pm_count', 'im_count',
        'movement_class', 
    ]

    for r in kept:
        r['movement_class'] = r['movement_class_3way']
        
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=final_fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(kept)

    print(f"Loaded:  {len(rows)} signs from {INPUT_FILE.name}")
    print(f"Dropped: {dropped} static signs")
    print(f"Kept:    {len(kept)} signs → {OUTPUT_FILE.name}")


if __name__ == '__main__':
    main()