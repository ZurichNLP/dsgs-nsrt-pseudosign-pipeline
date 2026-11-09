"""
Corpus-Level HamNoSys Structure Analysis

This file is to analyze structural patterns in 2,319 DSGS signs from step1 analysis_ready_pool, including parallel,
sequential, fusion, replacement, and repetition structures.

Compare their distributions across SS and CC signs, identify unusual structures,
and inform the design of structure-aware parameter extraction for pseudosign generation.

This script is for diagnostics only; it doesn't modify or generate signs.
"""


import csv
from pathlib import Path
from collections import Counter

# Locate the original Step 1 analysis pool.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = (
    PROJECT_ROOT
    / "step1_classification" / "output" / "analysis_ready_pool.csv"
)

# Structural markers that may affect pseudosign recombination. （from Hanke's 4.0 user guide, 2013)
PAR_OPEN = chr(0xE0E2)      # co-temporal (same time) or used in 2 handed signs []
PAR_CLOSE = chr(0xE0E3)

SEQ_OPEN = chr(0xE0E0)      # sequence
SEQ_CLOSE = chr(0xE0E1)

FUSION_OPEN = chr(0xE0E4)       # fused sequential <>
FUSION_CLOSE = chr(0xE0E5)

REPLACE = chr(0xE0AA)

REPETITIONS = {
    chr(cp) for cp in range(0xE0D8, 0xE0DD)
}

with open(INPUT_FILE, encoding="utf-8-sig", newline="") as f:  # sig is for BOM, to strengthen compatibility with Excel
    signs = list(csv.DictReader(f))

print(f"Total signs loaded: {len(signs)}")


def check_brackets(text, opening, closing):
    """Count bracket pairs, nesting, and unmatched markers."""

    stack = []
    pair_count = 0
    max_depth = 0
    unmatched_closes = 0

    for index, symbol in enumerate(text):

        if symbol == opening:
            stack.append(index)
            max_depth = max(max_depth, len(stack))

        elif symbol == closing:
            if stack:
                stack.pop()
                pair_count += 1
            else:
                unmatched_closes += 1

    return {
        "pairs": pair_count,
        "max_depth": max_depth,
        "unmatched_opens": len(stack),
        "unmatched_closes": unmatched_closes,
    }


def analyze_sign(row):
    """Extract structural features from one DSGS annotation."""

    text = row["hamnosys"]

    parallel = check_brackets(text, PAR_OPEN, PAR_CLOSE)
    sequence = check_brackets(text, SEQ_OPEN, SEQ_CLOSE)
    fusion = check_brackets(text, FUSION_OPEN, FUSION_CLOSE)

    hf = row["handshape_dsgs"]
    mov = row["movement_class"]

    # Keep the existing Step 1 classification.
    category = {
        ("simple", "simple"): "SS",
        ("simple", "complex"): "SC",
        ("complex", "simple"): "CS",
        ("complex", "complex"): "CC",
    }.get((hf, mov), "OTHER")

    return {
        "gloss_id": row["gloss_id"],
        "category": category,
        "handedness": row["handedness"],
        "pm_count": int(row["pm_count"]),
        "im_count": int(row["im_count"]),

        "has_parallel": parallel["pairs"] > 0,
        "parallel_pairs": parallel["pairs"],
        "parallel_depth": parallel["max_depth"],

        "has_replace": REPLACE in text,
        "replace_count": text.count(REPLACE),

        "has_sequence": sequence["pairs"] > 0,
        "has_fusion": fusion["pairs"] > 0,

        "has_repetition": any(
            symbol in REPETITIONS for symbol in text
        ),

        "unmatched_markers": any([
            parallel["unmatched_opens"],
            parallel["unmatched_closes"],
            sequence["unmatched_opens"],
            sequence["unmatched_closes"],
            fusion["unmatched_opens"],
            fusion["unmatched_closes"],
        ]),
    }


results = [analyze_sign(row) for row in signs]



def print_summary(rows, title):
    """Print structural statistics for one group of signs."""

    n = len(rows)

    print(f"\n{'=' * 55}")
    print(f"{title}: {n} signs")
    print("=" * 55)

    if n == 0:
        return

    features = [
        ("Parallel", "has_parallel"),
        ("Replacement", "has_replace"),
        ("Sequence", "has_sequence"),
        ("Fusion", "has_fusion"),
        ("Repetition", "has_repetition"),
        ("Nested parallel", None),
        ("Unmatched markers", "unmatched_markers"),
    ]

    for label, key in features:
        if key is None:
            count = sum(
                r["parallel_depth"] > 1 for r in rows
            )
        else:
            count = sum(r[key] for r in rows)

        print(f"{label:22s}: {count:4d} ({count/n:.1%})")

    handedness_counts = Counter(
        r["handedness"] for r in rows
    )
    print(f"\nHandedness: {dict(handedness_counts)}")

    parallel_counts = Counter(
        r["parallel_pairs"] for r in rows
    )
    print(
        "Parallel pair counts:",
        dict(sorted(parallel_counts.items()))
    )


# Overall classification distribution.
category_counts = Counter(r["category"] for r in results)

print("\nClassification distribution:")
for category in ["SS", "SC", "CS", "CC", "OTHER"]:
    print(f"{category}: {category_counts[category]}")

# Structural summaries.
print_summary(results, "ALL SIGNS")

ss = [r for r in results if r["category"] == "SS"]
cc = [r for r in results if r["category"] == "CC"]

print_summary(ss, "SS SIGNS")
print_summary(cc, "CC SIGNS")



def show_examples(rows, title, condition, limit=5):
    """Show real signs matching a structural condition."""

    matches = [r for r in rows if condition(r)]

    print(f"\n{title}: {len(matches)} signs")

    for r in matches[:limit]:
        print(
            f"  {r['gloss_id']}"
            f" | {r['category']}"
            f" | {r['handedness']}"
            f" | PM={r['pm_count']}, IM={r['im_count']}"
        )


# Identify examples for later manual inspection.
show_examples(
    cc, "CC with replacement",
    lambda r: r["has_replace"]
)

show_examples(
    cc, "CC without replacement",
    lambda r: not r["has_replace"]
)

show_examples(
    ss + cc, "Nested parallel structures",
    lambda r: r["parallel_depth"] > 1
)

show_examples(
    ss + cc, "Unmatched structural markers",
    lambda r: r["unmatched_markers"]
)

show_examples(
    ss + cc, "Signs with sequence structures",
    lambda r: r["has_sequence"]
)

show_examples(
    ss + cc, "Signs with fusion structures",
    lambda r: r["has_fusion"]
)
