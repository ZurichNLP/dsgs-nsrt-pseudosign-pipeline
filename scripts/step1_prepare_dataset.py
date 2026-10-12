"""
Step 1: Load, filter, and annotate DSGS glosses.

Input:  data/DSGS_glosses_HamNoSys.txt
        Tab-separated: gloss_id \t corpus_freq \t hamnosys_string

Output: output/cleaned_all.csv
          All signs with non-empty HamNoSys, plus flag columns.
        output/cleaned_analysis_pool.csv
          Pool A (inclusive, default): primary variants only, no fingerspelling, no pointing signs.
        output/cleaned_pool_ns1a_only.csv
          Pool B (conservative sanity check): only ns1a variant_letter=='A',
          no fingerspelling, no pointing signs.

Flags added:
  - variant_type       : 'primary' | 'secondary' | 'unparsed'
  - naming_style       : 'ns1a' | 'nsa1' | 'nsnum' | 'nosuffix'
                       | 'ns_composite' | 'unknown'
  - is_fingerspelled   : bool  (FA_ prefix)
  - is_pointing        : bool  (IX, POSS, DET types)
  - handedness         : 'single' | 'sym_two' | 'asym_two' | None
"""

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# --- Path setup ---
# This script lives in scripts/. Project root is one level up.
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'output'
CONFIG_DIR = PROJECT_ROOT / 'config'

# Load the classification dictionaries from config/.
sys.path.insert(0, str(CONFIG_DIR))
from hamnosys_dict import SYMMETRY_OPS, NON_DOMINANT_MARKER, ASYM_SEPARATOR

# Ensure output directory exists.
OUTPUT_DIR.mkdir(exist_ok=True)

INPUT_FILE       = DATA_DIR / 'DSGS_glosses_HamNoSys.txt'
OUT_ALL          = OUTPUT_DIR / 'cleaned_all.csv'
OUT_POOL_A       = OUTPUT_DIR / 'cleaned_analysis_pool.csv'   # inclusive
OUT_POOL_B       = OUTPUT_DIR / 'cleaned_pool_ns1a_only.csv'  # conservative


# --- Gloss ID parser ---
#
# DSGS dataset observed naming patterns:
#
#   ns1a          : WORD_[N][L]      → ABEND_1A, ABEND_1B, BESSER_1A
#                   traditional "sense number + variant letter"; A = primary
#
#   nsa1          : WORD_[L][N]      → BESSER_A4, AUSSCHMÜCKEN_A1, BODYGUARD_A1
#                   13 instances found. Evidence rules out typo hypothesis
#                   (12x _A1, 1x _A4; only 2 word_roots overlap with _[N]A;
#                   3 word_roots have _A[N] but no _[N]A). 
#                   Conservative: kept as primary.
#
#   nsnum         : WORD_[N]         → AUFWACHSEN_1, BEDAUERN_1
#                   number only, no letter. Likely "single sense, single variant".
#
#   nosuffix      : WORD             → AUFZÄHLEN, FLÜSSIG
#                   no suffix at all.
#
#   ns_composite  : WORD_[L][N].[N][L]  → SCHNAUZ_A1.1A
#                   composite/linked entry. Only 1 known instance.
#
#   unknown       : anything else with an underscore that matches no pattern
#                   → variant_type='unparsed'
#
GLOSS_PATTERN_1A        = re.compile(r'^(.+)_(\d+)([A-Z])$')
GLOSS_PATTERN_A1        = re.compile(r'^(.+)_([A-Z])(\d+)$')
GLOSS_PATTERN_NUM       = re.compile(r'^(.+)_(\d+)$')
GLOSS_PATTERN_COMPOSITE = re.compile(r'^(.+)_([A-Z])(\d+)\.(\d+)([A-Z])$')


def parse_gloss_id(gloss_id):
    """
    Parse a DSGS gloss ID into its structural components.
    Returns a dict with:
      word_root, sense_number, variant_letter, naming_style, variant_type

    Variant classification:
      ns1a          : letter == 'A' → primary; B/C/D... → secondary
      nsa1          : semantics unknown, conservatively marked primary
      nsnum         : no letter suffix → primary
      nosuffix      : standalone sign → primary
      ns_composite  : composite entry (only SCHNAUZ_A1.1A so far) → primary
      unknown       : has underscore but matches no pattern → unparsed
    """
    # 1. Composite (checked first because it contains substrings that
    #    would match GLOSS_PATTERN_1A and GLOSS_PATTERN_A1).
    m = GLOSS_PATTERN_COMPOSITE.match(gloss_id)
    if m:
        word_root, letter1, num1, num2, letter2 = m.groups()
        return {
            'word_root':      word_root,
            'sense_number':   int(num1),
            'variant_letter': f'{letter1}{num1}.{num2}{letter2}',
            'naming_style':   'ns_composite',
            'variant_type':   'primary',
        }

    # 2. WORD_1A
    m = GLOSS_PATTERN_1A.match(gloss_id)
    if m:
        word_root, sense_num, variant_letter = m.groups()
        return {
            'word_root':      word_root,
            'sense_number':   int(sense_num),
            'variant_letter': variant_letter,
            'naming_style':   'ns1a',
            'variant_type':   'primary' if variant_letter == 'A' else 'secondary',
        }

    # 3. WORD_A1
    m = GLOSS_PATTERN_A1.match(gloss_id)
    if m:
        word_root, letter, num = m.groups()
        return {
            'word_root':      word_root,
            'sense_number':   int(num),
            'variant_letter': letter,
            'naming_style':   'nsa1',
            'variant_type':   'primary',
        }

    # 4. WORD_1
    m = GLOSS_PATTERN_NUM.match(gloss_id)
    if m:
        word_root, num = m.groups()
        return {
            'word_root':      word_root,
            'sense_number':   int(num),
            'variant_letter': None,
            'naming_style':   'nsnum',
            'variant_type':   'primary',
        }

    # 5. no underscore → standalone sign
    if '_' not in gloss_id:
        return {
            'word_root':      gloss_id,
            'sense_number':   None,
            'variant_letter': None,
            'naming_style':   'nosuffix',
            'variant_type':   'primary',
        }

    # 6. has underscore but matches no known pattern → truly unparsed
    return {
        'word_root':      gloss_id,
        'sense_number':   None,
        'variant_letter': None,
        'naming_style':   'unknown',
        'variant_type':   'unparsed',
    }


# --- Handedness detection ---

def detect_handedness(hamnosys_str):
    """
    Handedness rules:
      - Starts with symmetry operator (E0E8/E0E9)     -> sym_two
      - Contains ASYM_SEPARATOR (E0E7)             -> asym_two
        (Guide §9: [dominant ≠ non-dominant] structure. 
        Signbank sometimes omits the outer [ ] brackets.)
      - This branch also covers the 5 signs containing
        hamnondominant (E0EA) mid-sign, since they all contain ≠.
      - Otherwise                                     -> single
    Precedence: sym_op > E0E7 > E0EA. Symmetric signs may contain E0E7
    inside brackets to differentiate specific parameters (e.g., location)
    per Guide §9.2, but they remain sym_two.
    """
    if not hamnosys_str:
        return None
    codepoints = [ord(c) for c in hamnosys_str]
    if codepoints[0] in SYMMETRY_OPS:
        return 'sym_two'
    if ASYM_SEPARATOR in codepoints:
        return 'asym_two'
    return 'single'


# --- Semantic-class flags ---
def is_fingerspelled(gloss_id):
    """Fingerspelling: gloss_id starts with 'FA_'."""
    return gloss_id.startswith('FA_')


POINTING_PREFIXES = ('IX_', 'IX-', 'POSS_', 'POSS-', 'DET_', 'DET-')

def is_pointing(gloss_id):
    """Pointing/grammatical: IX, POSS, DET (and variants)."""
    return gloss_id.startswith(POINTING_PREFIXES)
#   I also checked other prefixes here, e.g., "LOC", "PRO".

# --- Main pipeline ---
def load_and_annotate():
    """Read the input file, filter empty rows, add annotation columns."""
    rows = []
    total_read = 0
    skipped_empty = 0

    with open(INPUT_FILE, encoding='utf-8') as f:
        for line in f:
            total_read += 1
            line = line.rstrip('\n')
            if not line:
                skipped_empty += 1
                continue

            # Split into 3 columns; be defensive about extra tabs.
            parts = line.split('\t')
            if len(parts) < 3:
                skipped_empty += 1
                continue

            gloss_id = parts[0].strip()
            try:
                corpus_freq = int(parts[1].strip())
            except ValueError:
                corpus_freq = 0
            hamnosys = parts[2].strip()

            if not hamnosys:
                skipped_empty += 1
                continue

            parsed = parse_gloss_id(gloss_id)

            rows.append({
                'gloss_id':         gloss_id,
                'corpus_freq':      corpus_freq,
                'hamnosys':         hamnosys,
                'word_root':        parsed['word_root'],
                'sense_number':     parsed['sense_number'],
                'variant_letter':   parsed['variant_letter'],
                'naming_style':     parsed['naming_style'],
                'variant_type':     parsed['variant_type'],
                'is_fingerspelled': is_fingerspelled(gloss_id),
                'is_pointing':      is_pointing(gloss_id),
                'handedness':       detect_handedness(hamnosys),
                'hamnosys_length':  len(hamnosys),
            })

    return rows, total_read, skipped_empty


def write_csv(rows, out_path):
    """Write rows (list of dicts) to a CSV file."""
    if not rows:
        print(f"  (no rows to write to {out_path.name})")
        return
    fieldnames = list(rows[0].keys())
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(label, rows):
    """Print quick counts for a set of rows."""
    print(f"\n{label}: {len(rows)} signs")
    print(f"  variant_type:     {dict(Counter(r['variant_type']       for r in rows))}")
    print(f"  naming_style:     {dict(Counter(r['naming_style']       for r in rows))}")
    print(f"  is_fingerspelled: {dict(Counter(r['is_fingerspelled']   for r in rows))}")
    print(f"  is_pointing:      {dict(Counter(r['is_pointing']        for r in rows))}")
    print(f"  handedness:       {dict(Counter(r['handedness']         for r in rows))}")


def diagnose_base_collisions(rows):
    """
    Find word_roots that appear under multiple naming_styles.
    Tells us whether different styles are potentially duplicate variants
    of the same underlying sign (evidence for the pool filter decision).

    Fingerspelled entries are excluded to avoid FA_ prefix noise.
    """
    root_to_styles = defaultdict(set)
    for r in rows:
        if r['is_fingerspelled']:
            continue
        root_to_styles[r['word_root']].add(r['naming_style'])

    conflicts = {root: styles for root, styles in root_to_styles.items()
                 if len(styles) > 1}

    print(f"\n--- Base collision diagnostic ---")
    print(f"  Unique word_roots (non-FA):     {len(root_to_styles)}")
    print(f"  Roots with multiple styles:     {len(conflicts)}")

    if not conflicts:
        print(f"  No collisions found. All naming_styles are disjoint.")
        return

    combo_counter = Counter()
    combo_examples = defaultdict(list)
    for root, styles in conflicts.items():
        combo = tuple(sorted(styles))
        combo_counter[combo] += 1
        if len(combo_examples[combo]) < 5:
            combo_examples[combo].append(root)

    print(f"\n  Style combinations:")
    for combo, n in combo_counter.most_common():
        print(f"    {' + '.join(combo):40s} {n:4d} roots")

    print(f"\n  Examples (up to 5 per combination):")
    for combo, examples in combo_examples.items():
        print(f"    [{' + '.join(combo)}]")
        for ex in examples:
            print(f"      {ex}")


def main():
    print(f"Reading:  {INPUT_FILE}")
    if not INPUT_FILE.exists():
        print(f"ERROR: input file not found at {INPUT_FILE}")
        sys.exit(1)

    rows, total_read, skipped_empty = load_and_annotate()

    print(f"\n--- Load summary ---")
    print(f"  Lines read:                    {total_read}")
    print(f"  Skipped (empty HamNoSys / no): {skipped_empty}")
    print(f"  Kept (non-empty HamNoSys):     {len(rows)}")

    # Full annotated set
    write_csv(rows, OUT_ALL)
    print(f"\nWrote: {OUT_ALL}")
    print_summary("Full annotated set (cleaned_all)", rows)

    # Base collision diagnostic
    diagnose_base_collisions(rows)

    # ------------------------------------------------------------------
    # Pool A (inclusive, default): primary variants, no fingerspelling.
    #   Includes ns1a(A), nsa1, nsnum, nosuffix, ns_composite.
    #   Rationale: candidate pool for handshape × movement statistics.
    #   Cost of false positives (duplicate variants) < cost of false negatives 
    #   (dropping genuinely independent signs).
    #
    # Pointing signs (IX, POSS, DET) are retained via is_pointing flag.
    #   They are grammatical function words and would all fall into the
    #   SS cell, potentially skewing the distribution, but they are also
    #   central to child sign language acquisition. Toggle at analysis time.
    # ------------------------------------------------------------------

    pool_a = [r for r in rows
              if r['variant_type'] == 'primary'
              and not r['is_fingerspelled']
              and not r['is_pointing']
              and r['hamnosys'] != '\u221A'                 # KEGELN_1A: data error
              and not r['gloss_id'].startswith('$PROD_')    # productive constructions
            ]
    write_csv(pool_a, OUT_POOL_A)
    print(f"\nWrote: {OUT_POOL_A}")
    print_summary("Pool A (inclusive, default)", pool_a)

    # ------------------------------------------------------------------
    # Pool B (conservative sanity check): only traditional ns1a with
    #   variant_letter=='A', no fingerspelling.
    #   Use for cross-checking whether Pool A's non-ns1a additions
    #   introduce systematic bias in handshape × movement distribution.
    # ------------------------------------------------------------------
    pool_b = [r for r in rows
              if r['naming_style'] == 'ns1a'
              and r['variant_letter'] == 'A'
              and not r['is_fingerspelled']
              and not r['is_pointing']
              and r['hamnosys'] != '\u221A'                 # KEGELN_1A: data error
              and not r['gloss_id'].startswith('$PROD_')    # productive constructions
            ]
    write_csv(pool_b, OUT_POOL_B)
    print(f"\nWrote: {OUT_POOL_B}")
    print_summary("Pool B (ns1a-A only, conservative)", pool_b)

    # Delta
    print(f"\n--- Pool A vs Pool B ---")
    print(f"  Pool A size: {len(pool_a)}")
    print(f"  Pool B size: {len(pool_b)}")
    print(f"  Delta (A - B, i.e. rows we kept conservatively): {len(pool_a) - len(pool_b)}")


if __name__ == '__main__':
    main()