
"""Run movement extraction across the DSGS corpus."""

import csv
from collections import Counter
from pathlib import Path

from movement_extraction import (
    extract_complete_movement,
    to_codepoints,
)


ROOT = Path(__file__).resolve().parent

INPUT_FILE = (
    ROOT.parent
    / "step1_classification"
    / "output"
    / "analysis_ready_pool.csv"
)

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

RESULTS_FILE = OUTPUT_DIR / "movement_extraction_results.csv"
REVIEW_FILE = OUTPUT_DIR / "movement_extraction_review.csv"


def get_group(row):
    """Return the Step 1 handshape/movement combination."""

    hs = row["handshape_dsgs"]
    mov = row["movement_class"]

    labels = {"simple": "S", "complex": "C"}

    return labels.get(hs, "?") + labels.get(mov, "?")


def check_result(original, result):
    """Flag results that require boundary inspection."""

    flags = []

    if result is None:
        return ["extraction_failed"]

    prefix = (
        result["symmetry"]
        + result["hf"]
        + result["hp"]
        + result["loc"]
    )

    if prefix + result["mov"] != original:
        flags.append("reconstruction_mismatch")

    if not result["mov"]:
        flags.append("empty_movement")

    # Movement must not begin with a closing bracket.
    if result["mov"] and ord(result["mov"][0]) in {
        0xE0E1, 0xE0E3, 0xE0E5
    }:
        flags.append("closing_bracket_at_start")

    # Review complex handedness and structural boundaries.
    if chr(0xE0E7) in original:
        flags.append("asymmetric_two_handed")

    if result["mov"].startswith(chr(0xE0E2)):
        flags.append("parallel_movement")

    if chr(0xE0AA) in result["mov"]:
        flags.append("replacement_in_movement")

    # This is a review flag, not proof of an error.
    if result["loc"] == "":
        flags.append("no_initial_location")

    return flags


def main():

    with open(INPUT_FILE, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    results = []
    review = []

    for row in rows:

        original = row["hamnosys"]
        error = ""

        try:
            extracted = extract_complete_movement(original)

        except Exception as exc:
            extracted = None
            error = f"{type(exc).__name__}: {exc}"

        flags = check_result(original, extracted)

        output = {
            "gloss_id": row["gloss_id"],
            "group": get_group(row),
            "handedness": row["handedness"],
            "original_hamnosys": original,
            "original_codepoints": to_codepoints(original),
            "status": "unresolved" if extracted is None else "candidate",
            "symmetry": "",
            "hf": "",
            "hp": "",
            "loc": "",
            "mov": "",
            "mov_codepoints": "",
            "parser_matches_count": 0,
            "review_flags": "; ".join(flags),
            "error": error,
        }

        if extracted is not None:
            output.update({
                "symmetry": extracted["symmetry"],
                "hf": extracted["hf"],
                "hp": extracted["hp"],
                "loc": extracted["loc"],
                "mov": extracted["mov"],
                "mov_codepoints": to_codepoints(extracted["mov"]),
                "parser_matches_count": len(
                    extracted["parser_matches"]
                ),
            })

        results.append(output)

        if flags:
            review.append(output.copy())

    # Save the complete extraction results.
    fields = list(results[0].keys())

    with open(RESULTS_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    with open(REVIEW_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(review)

    # Report overall outcomes.
    print("\n=== CORPUS EXTRACTION SUMMARY ===")
    print(f"Total signs: {len(results)}")

    status_counts = Counter(r["status"] for r in results)

    for status, count in status_counts.items():
        print(f"{status}: {count}")

    print("\n=== BY COMPLEXITY GROUP ===")

    for group in ["SS", "SC", "CS", "CC", "??"]:
        subset = [r for r in results if r["group"] == group]

        if not subset:
            continue

        candidates = sum(
            r["status"] == "candidate" for r in subset
        )

        print(f"{group}: {candidates}/{len(subset)} candidates")

    print("\n=== REVIEW FLAGS ===")

    flag_counts = Counter(
        flag.strip()
        for r in results
        for flag in r["review_flags"].split(";")
        if flag.strip()
    )

    for flag, count in flag_counts.most_common():
        print(f"{flag}: {count}")

    print("\n=== SAMPLE CANDIDATES ===")

    for group in ["SS", "CC"]:
        examples = [
            r for r in results
            if r["group"] == group
            and r["status"] == "candidate"
        ][:5]

        print(f"\n{group}:")

        for item in examples:
            print(f"  {item['gloss_id']}")
            print(f"  MOV: {item['mov_codepoints']}")
            print(f"  Flags: {item['review_flags']}")

    print(f"\nResults: {RESULTS_FILE}")
    print(f"Review:  {REVIEW_FILE}")


if __name__ == "__main__":
    main()
