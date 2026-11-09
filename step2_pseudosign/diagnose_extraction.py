
"""Diagnose common extraction failures and structural risks."""

import csv
from collections import Counter, defaultdict
from pathlib import Path

import movement_extraction as me


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

REVIEW_FILE = OUTPUT_DIR / "extraction_review.csv"
SOURCE_FILE = OUTPUT_DIR / "source_parameters.csv"
DIAGNOSTIC_FILE = OUTPUT_DIR / "extraction_failure_diagnostics.csv"


def read_csv(path):
    """Read a CSV file as dictionaries."""
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def codepoints(text, limit=12):
    """Show the first Unicode codepoints of a string."""
    if not text:
        return "(empty)"

    chars = [f"U+{ord(c):04X}" for c in text[:limit]]
    suffix = " ..." if len(text) > limit else ""
    return " ".join(chars) + suffix


def inspect_failure(hamnosys):
    """Locate the stage where parameter extraction stops."""
    remaining = hamnosys
    symmetry = ""

    if remaining and ord(remaining[0]) in me.SYMMETRY_OPS:
        symmetry = remaining[0]
        remaining = remaining[1:]

    hf = ""
    hp = ""
    loc = ""

    try:
        hf = me.prefix_match(
            me.getHandform(remaining, me.BETWEEN, me.REPETITIONS),
            remaining,
        )
        if not hf:
            return "HF", remaining, hf, hp, loc

        remaining = remaining[len(hf):]

        hp = me.prefix_match(
            me.getHandposition(
                remaining, me.BETWEEN, me.REPETITIONS,
                me.CONTACT, me.ALTERNATING, me.SPEEDS,
            ),
            remaining,
        )
        if not hp:
            return "HP", remaining, hf, hp, loc

        remaining = remaining[len(hp):]

        loc = me.prefix_match(
            me.getLocation(
                remaining, me.BETWEEN,
                me.CONTACT, me.REPETITIONS,
            ),
            remaining,
        ) or ""

        remaining = remaining[len(loc):]

        if not remaining:
            return "EMPTY_MOV", remaining, hf, hp, loc

        matches = me.getMovement(
            remaining, me.BETWEEN, me.SIZES,
            me.SPEEDS, me.REPETITIONS, me.CONTACT,
        )

        if not matches:
            return "MOV", remaining, hf, hp, loc

        return "MATCHED", remaining, hf, hp, loc

    except Exception:
        return "PARSER_ERROR", remaining, hf, hp, loc


def diagnose_unresolved(review_rows):
    """Group unresolved signs by failing-stage prefixes."""
    failures = [
        row for row in review_rows
        if row["status"] == "unresolved"
    ]

    grouped = defaultdict(list)
    details = []

    for row in failures:
        stage, remaining, hf, hp, loc = inspect_failure(
            row["hamnosys"]
        )

        prefix = codepoints(remaining[:2])
        key = (row["reason"], prefix)

        grouped[key].append(row["gloss_id"])

        details.append({
            "gloss_id": row["gloss_id"],
            "group": row["group"],
            "handedness": row["handedness"],
            "reason": row["reason"],
            "failed_stage": stage,
            "remaining_prefix": prefix,
            "remaining_codepoints": codepoints(remaining, 40),
            "hf_codepoints": codepoints(hf),
            "hp_codepoints": codepoints(hp),
            "loc_codepoints": codepoints(loc),
            "hamnosys": row["hamnosys"],
        })

    print("\n=== UNRESOLVED SIGNS ===")
    print(f"Total: {len(failures)}")

    for reason in (
        "hf_not_found",
        "hp_not_found",
        "mov_not_recognised",
    ):
        subset = [
            (prefix, ids)
            for (r, prefix), ids in grouped.items()
            if r == reason
        ]

        subset.sort(key=lambda item: len(item[1]), reverse=True)

        total = sum(len(ids) for _, ids in subset)
        print(f"\n{reason}: {total}")

        print("Most common prefixes at the failing stage:")
        for prefix, ids in subset[:8]:
            print(f"  {len(ids):3d}  {prefix}")
            print(f"       Examples: {', '.join(ids[:3])}")

    if details:
        fields = list(details[0].keys())
        with DIAGNOSTIC_FILE.open(
            "w", encoding="utf-8-sig", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(details)

    print(f"\nDetailed failures: {DIAGNOSTIC_FILE}")


def inspect_two_handed(source_rows):
    """Show representative extracted two-handed structures."""
    print("\n=== TWO-HANDED STRUCTURES ===")

    for label, condition in (
        (
            "SYMMETRIC",
            lambda r: r["handedness"] == "sym_two",
        ),
        (
            "ASYMMETRIC / E0E7",
            lambda r: (
                r["handedness"] == "asym_two"
                or chr(0xE0E7) in r["hamnosys"]
            ),
        ),
    ):
        matches = [r for r in source_rows if condition(r)]
        print(f"\n{label}: {len(matches)} extracted signs")

        for row in matches[:5]:
            print(f"\n  {row['gloss_id']} ({row['group']})")
            print("  Symmetry:", codepoints(row["symmetry"]))
            print("  HF:      ", codepoints(row["hf"]))
            print("  HP:      ", codepoints(row["hp"]))
            print("  LOC:     ", codepoints(row["loc"]))
            print("  MOV:     ", codepoints(row["mov"], 30))


def main():
    review_rows = read_csv(REVIEW_FILE)
    source_rows = read_csv(SOURCE_FILE)

    diagnose_unresolved(review_rows)
    inspect_two_handed(source_rows)


if __name__ == "__main__":
    main()
