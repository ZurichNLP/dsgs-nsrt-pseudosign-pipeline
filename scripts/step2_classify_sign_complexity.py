"""
Step 2: Classify each DSGS sign by handshape and movement complexity.

Input:  output/cleaned_analysis_pool.csv  (Pool A from Step 1, 3432 signs)
Output: output/classified_details.csv

Classification framework: Mann & Marshall (2010), Section 3.4.
  Handshape:
    - Simple (BSL): B, 5, G, A  (Sutton-Spence & Woll 1999)
    - Simple (DSGS): + C, O     (Boyes Braem 1995)
  Movement:
    - Simple:  one movement (PM or IM alone)
    - Complex: PM + IM co-temporal (movement cluster)
  "complex" is applied strictly: only PM+IM inside the same [...] bracket counts as complex. 
  Sequential PM+PM, fusion <...>, and PM+IM outside [...] 
  are all classified as simple.

  Static signs (no PM and no IM) fall outside Mann 2010's design; three
  movement class versions are output so Step 3 can compare treatments.

HamNoSys structure reference: Smith (2013) HamNoSys 4.0 User Guide.
  §2 general structure, §7 movements,
  §8 brackets ([ ] = co-temporal), §9 two-handed signs.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

# --- Path setup ---
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / 'output'
CONFIG_DIR = PROJECT_ROOT / 'config'

sys.path.insert(0, str(CONFIG_DIR))
from hamnosys_dict import (
    BASE_HANDSHAPES,
    SIMPLE_HANDSHAPES_BSL4,
    SIMPLE_HANDSHAPES_DSGS6,
    PM_ALL,
    IM_ALL,
    SYMMETRY_OPS,
    NON_DOMINANT_MARKER,
    ASYM_SEPARATOR,
    COTEMPORAL_OPEN,
    COTEMPORAL_CLOSE,
)

INPUT_FILE  = OUTPUT_DIR / 'cleaned_analysis_pool.csv'
OUTPUT_FILE = OUTPUT_DIR / 'classified_details.csv'



# ---- STAGE 1: Find where the dominant hand's description starts ----


def find_dominant_start(hamnosys_str):
    """
    Return the string index where the dominant hand's description begins.

    Per Guide §2 and §9:
      - Two-handed symmetric sign: starts with a symmetry operator; the
        description that follows is for the dominant hand.
      - Two-handed asymmetric sign: [dominant ≠ non-dominant]; the
        dominant hand's description follows an opening [.
      - Single-handed sign: description starts at index 0.
    """
    if not hamnosys_str:
        return 0

    first_cp = ord(hamnosys_str[0])
    if first_cp in SYMMETRY_OPS or first_cp == COTEMPORAL_OPEN:
        return 1
    if first_cp == ASYM_SEPARATOR:  # (rare: PLAN_1A, Guide §9.2 variant)
        return 1
    return 0



# ---- STAGE 2: Extract the base handshape of the dominant hand ----


def extract_base_handshape(hamnosys_str, handedness):
    """
    Return the codepoint of the first base handshape in the dominant hand's
    description, or None if none found.

    Stops at ASYM_SEPARATOR (in asym_two signs only) or NON_DOMINANT_MARKER,
    to avoid picking up the non-dominant hand's handshape.
    """
    start = find_dominant_start(hamnosys_str)

    for i in range(start, len(hamnosys_str)):
        cp = ord(hamnosys_str[i])
        if cp == NON_DOMINANT_MARKER:
            return None
        if cp == ASYM_SEPARATOR and handedness == 'asym_two':
            return None
        if cp in BASE_HANDSHAPES:
            return cp

    return None


# ---- STAGE 3: Classify the handshape (BSL 4 + DSGS 6) ----


def classify_handshape(base_cp):
    """
    Return (is_simple_bsl, is_simple_dsgs) for the given base handshape.
    Returns (None, None) if base_cp is None.
    """
    if base_cp is None:
        return None, None
    return (base_cp in SIMPLE_HANDSHAPES_BSL4), (base_cp in SIMPLE_HANDSHAPES_DSGS6)


# ---- STAGE 4: Extract PM and IM positions in the dominant hand's description ----


def extract_movements(hamnosys_str, handedness):
    """
    Return (pm_positions, im_positions): lists of string indices where PM and
    IM symbols occur in the dominant hand's description.

    Stops at ASYM_SEPARATOR (in asym_two signs only) or NON_DOMINANT_MARKER,
    so non-dominant hand's movements don't enter the classification.
    """
    start = find_dominant_start(hamnosys_str)

    pm_positions = []
    im_positions = []

    for i in range(start, len(hamnosys_str)):
        cp = ord(hamnosys_str[i])
        if cp == NON_DOMINANT_MARKER:
            break
        if cp == ASYM_SEPARATOR and handedness == 'asym_two':
            break
        if cp in PM_ALL:
            pm_positions.append(i)
        elif cp in IM_ALL:
            im_positions.append(i)

    return pm_positions, im_positions



# ---- STAGE 5: Detect co-temporal PM+IM (Mann's movement cluster) ----


def find_bracket_pairs(hamnosys_str, start_idx):
    """
    Return a list of (open_idx, close_idx) tuples for matched [...] pairs
    from start_idx onward. Uses a stack to handle nesting; unmatched brackets
    are silently dropped.

    Note on two-handed asymmetric signs: the leading [ has been skipped by
    Stage 1, so its matching ] later in the string will find an empty stack
    and be discarded, which is the intended behavior.
    """
    pairs = []
    stack = []

    for i in range(start_idx, len(hamnosys_str)):
        cp = ord(hamnosys_str[i])
        if cp == COTEMPORAL_OPEN:
            stack.append(i)
        elif cp == COTEMPORAL_CLOSE:
            if stack:
                pairs.append((stack.pop(), i))

    return pairs


def has_cotemporal_pm_im(hamnosys_str, pm_positions, im_positions, handedness):
    """
    Return True if any [...] bracket pair contains at least one PM position
    and at least one IM position simultaneously.
    For asym_two signs: brackets containing ASYM_SEPARATOR are skipped,
    because [dom ≠ non-dom] is a two-handed structure (Guide §9), not a
    co-temporal movement cluster.
    """
    if not pm_positions or not im_positions:
        return False

    start = find_dominant_start(hamnosys_str)
    for open_idx, close_idx in find_bracket_pairs(hamnosys_str, start):
        if handedness == 'asym_two':
            bracket_content = hamnosys_str[open_idx+1:close_idx]
            if any(ord(c) == ASYM_SEPARATOR for c in bracket_content):
                continue
        pm_inside = any(open_idx < p < close_idx for p in pm_positions)
        im_inside = any(open_idx < p < close_idx for p in im_positions)
        if pm_inside and im_inside:
            return True

    return False


# ---- STAGE 6: Classify movement (three versions for Step 3 comparison) ----


def classify_movement(hamnosys_str, pm_positions, im_positions, handedness):
    """
    Return (movement_class_3way, movement_class_strict, movement_class_excluded).

    3way:     'static' | 'simple' | 'complex'   — full information
    strict:   'simple' | 'complex'              — static folded into simple
    excluded: 'simple' | 'complex' | 'excluded' — static dropped from 2x2

    According to Mann 2010 §3.4 (strict): only PM+IM co-temporal counts as complex.
    Static (no movement) is outside Mann's design.
    """
    if not pm_positions and not im_positions:
        return 'static', 'simple', 'excluded'

    if has_cotemporal_pm_im(hamnosys_str, pm_positions, im_positions, handedness):
        return 'complex', 'complex', 'complex'

    return 'simple', 'simple', 'simple'


# ---- MAIN PIPELINE ----


def classify_row(row):
    """Apply the full pipeline to one Step 1 row."""
    hamnosys_str = row['hamnosys']
    handedness = row['handedness']

    base_cp = extract_base_handshape(hamnosys_str, handedness)
    is_simple_bsl, is_simple_dsgs = classify_handshape(base_cp)
    pm_positions, im_positions = extract_movements(hamnosys_str, handedness)
    mv_3way, mv_strict, mv_excluded = classify_movement(
        hamnosys_str, pm_positions, im_positions, handedness
    )

    return {
        # Carry-over from Step 1
        'gloss_id':         row['gloss_id'],
        'corpus_freq':      row['corpus_freq'],
        'hamnosys':         hamnosys_str,
        'hamnosys_length':  row['hamnosys_length'],
        'naming_style':     row['naming_style'],
        'handedness':       row['handedness'],
        'is_pointing':      row['is_pointing'],

        # Handshape classification
        'base_handshape_cp': f'U+{base_cp:04X}' if base_cp is not None else '',
        'handshape_bsl':     ('simple' if is_simple_bsl else 'complex')
                             if is_simple_bsl is not None else '',
        'handshape_dsgs':    ('simple' if is_simple_dsgs else 'complex')
                             if is_simple_dsgs is not None else '',

        # Movement classification
        'pm_count':               len(pm_positions),
        'im_count':               len(im_positions),
        'movement_class_3way':    mv_3way,
        'movement_class_strict':  mv_strict,
        'movement_class_excluded': mv_excluded,
    }


def print_diagnostics(rows):
    """Print distribution summaries to sanity-check the classification."""
    print(f"\n--- Classification diagnostics ---")
    print(f"Total classified: {len(rows)}")

    hs_bsl  = Counter(r['handshape_bsl']  or 'MISSING' for r in rows)
    hs_dsgs = Counter(r['handshape_dsgs'] or 'MISSING' for r in rows)
    print(f"\nHandshape (BSL 4):  {dict(hs_bsl)}")
    print(f"Handshape (DSGS 6): {dict(hs_dsgs)}")

    mv_3way = Counter(r['movement_class_3way'] for r in rows)
    print(f"\nMovement (3-way):   {dict(mv_3way)}")

    pm_dist = Counter(r['pm_count'] for r in rows)
    im_dist = Counter(r['im_count'] for r in rows)
    print(f"\nPM count distribution: {dict(sorted(pm_dist.items()))}")
    print(f"IM count distribution: {dict(sorted(im_dist.items()))}")

    print(f"\n--- 2x2 distribution (BSL 4 handshape) ---")
    _print_2x2(rows, 'handshape_bsl', 'movement_class_strict',   'STRICT (static -> simple)')
    _print_2x2(rows, 'handshape_bsl', 'movement_class_excluded', 'EXCLUDED (static dropped)')

    print(f"\n--- 2x2 distribution (DSGS 6 handshape) ---")
    _print_2x2(rows, 'handshape_dsgs', 'movement_class_strict',   'STRICT (static -> simple)')
    _print_2x2(rows, 'handshape_dsgs', 'movement_class_excluded', 'EXCLUDED (static dropped)')

    missing_hs = [r for r in rows if not r['base_handshape_cp']]
    print(f"\nSigns with no base handshape found: {len(missing_hs)}")
    if missing_hs:
        print(f"  Examples (first 10):")
        for r in missing_hs[:10]:
            print(f"    {r['gloss_id']:30s} len={r['hamnosys_length']}")


def _print_2x2(rows, hs_field, mv_field, label):
    """Print a 2x2 contingency table."""
    print(f"\n  [{label}]")
    counts = Counter()
    for r in rows:
        hs, mv = r[hs_field], r[mv_field]
        if hs and mv and mv != 'excluded':
            counts[(hs, mv)] += 1

    total = sum(counts.values())
    print(f"                    Simple movement   Complex movement   Row total")
    for hs in ['simple', 'complex']:
        s = counts[(hs, 'simple')]
        c = counts[(hs, 'complex')]
        print(f"  {hs:8s} handshape:   {s:6d}            {c:6d}         {s + c:6d}")
    col_s = counts[('simple', 'simple')] + counts[('complex', 'simple')]
    col_c = counts[('simple', 'complex')] + counts[('complex', 'complex')]
    print(f"  Column total:      {col_s:6d}            {col_c:6d}         {total:6d}")


def main():
    print(f"Reading:  {INPUT_FILE}")
    if not INPUT_FILE.exists():
        print(f"ERROR: input file not found at {INPUT_FILE}")
        sys.exit(1)

    with open(INPUT_FILE, encoding='utf-8') as f:
        input_rows = list(csv.DictReader(f))

    print(f"  Loaded {len(input_rows)} signs from Pool A.")

    classified = [classify_row(r) for r in input_rows]

    fieldnames = list(classified[0].keys())
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified)

    print(f"\nWrote: {OUTPUT_FILE}")
    print_diagnostics(classified)


if __name__ == '__main__':
    main()