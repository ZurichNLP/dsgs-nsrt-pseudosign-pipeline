
"""Diagnose extraction failures and generate 10 pilot SS candidates."""

import csv
from collections import Counter
from pathlib import Path

from movement_extraction import (
    extract_complete_movement,
    getHandform,
    getHandposition,
    getLocation,
    getMovement,
    prefix_match,
    to_codepoints,
    BETWEEN,
    REPETITIONS,
    CONTACT,
    SPEEDS,
    SIZES,
    ALTERNATING,
)


ROOT = Path(__file__).resolve().parent
INPUT = (
    ROOT.parent
    / "step1_classification"
    / "output"
    / "analysis_ready_pool.csv"
)

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

CANDIDATES_FILE = OUTPUT_DIR / "pilot_ss_A.csv"
DIAGNOSTICS_FILE = OUTPUT_DIR / "extraction_diagnostics.csv"

# Movement symbols that can begin a simple movement.
PM_PRIMARY = set(range(0xE080, 0xE0A4))
IM_PRIMARY = set(range(0xE0A4, 0xE0AA))
MOV_START = PM_PRIMARY | IM_PRIMARY

# For this pilot, defer structures requiring extra rules.
SPECIAL = set(range(0xE0E0, 0xE0EB)) | {0xE0AA} 


def diagnose(hamnosys):
    """Find the first stage where extraction stops."""

    remaining = hamnosys

    # Remove an initial symmetry marker, if present.
    if remaining and ord(remaining[0]) in {0xE0E8, 0xE0E9}:
        remaining = remaining[1:]

    hf = prefix_match(
        getHandform(remaining, BETWEEN, REPETITIONS),
        remaining
    )

    if not hf:
        return "HF"

    remaining = remaining[len(hf):]

    hp = prefix_match(
        getHandposition(
            remaining, BETWEEN, REPETITIONS,
            CONTACT, ALTERNATING, SPEEDS
        ),
        remaining
    )

    if not hp:
        return "HP"

    remaining = remaining[len(hp):]

    loc = prefix_match(
        getLocation(
            remaining, BETWEEN, CONTACT, REPETITIONS
        ),
        remaining
    )

    if loc:
        remaining = remaining[len(loc):]

    if not remaining:
        return "MOV_empty"

    matches = getMovement(
        remaining, BETWEEN, SIZES, SPEEDS,
        REPETITIONS, CONTACT
    )

    if not matches:
        return "MOV_not_recognised"

    return "other"


def eligible_source(row, result):
    """Apply conservative pilot-only extraction checks."""

    if row["handedness"] != "single":
        return False

    if not result:
        return False

    if result["symmetry"]:
        return False

    if not all(result[k] for k in ("hf", "hp", "loc", "mov")):
        return False

    original = row["hamnosys"]
    mov = result["mov"]

    if any(ord(ch) in SPECIAL for ch in original):
        return False

    if ord(mov[0]) not in MOV_START:
        return False

    # Require a complete match, not merely a partial movement match.
    if result["parser_matches"] != [mov]:
        return False

    if result["hf"] + result["hp"] + result["loc"] + mov != original:
        return False

    return True


def main():
    with open(INPUT, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    diagnostic_rows = []
    extracted_rows = []
    failure_counts = Counter()

    # Part 1: Diagnose the full corpus.
    for row in rows:
        original = row["hamnosys"]

        try:
            result = extract_complete_movement(original)
            error = ""
        except Exception as exc:
            result = None
            error = f"{type(exc).__name__}: {exc}"

        if result is None:
            try:
                stage = diagnose(original)
            except Exception as exc:
                stage = "diagnostic_error"
                error += f" | {type(exc).__name__}: {exc}"

            failure_counts[stage] += 1
        else:
            stage = "candidate"

        diagnostic_rows.append({
            "gloss_id": row["gloss_id"],
            "handedness": row["handedness"],
            "handshape_dsgs": row["handshape_dsgs"],
            "movement_class": row["movement_class"],
            "status": stage,
            "error": error,
            "codepoints": to_codepoints(original),
        })

        extracted_rows.append((row, result))

    fields = list(diagnostic_rows[0])

    with open(
        DIAGNOSTICS_FILE, "w",
        encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(diagnostic_rows)

    print("\n=== EXTRACTION FAILURES ===")

    for reason, count in failure_counts.most_common():
        print(f"{reason}: {count}")

    # Part 2: Select conservative SS sources.
    ss_sources = [
        (row, result)
        for row, result in extracted_rows
        if row["handshape_dsgs"] == "simple"
        and row["movement_class"] == "simple"
        and eligible_source(row, result)
    ]

    print(f"\nPilot-eligible SS sources: {len(ss_sources)}")

    # Part 3: Generate category-A candidates. HF and MOV from one source, HP and LOC from another.
    original_strings = {row["hamnosys"] for row in rows}
    seen = set()
    candidates = []
    source_a_counts = Counter()

    for row_a, a in ss_sources:
        for row_b, b in ss_sources:

            if row_a["gloss_id"] == row_b["gloss_id"]:
                continue

            new_sign = (
                a["hf"]
                + b["hp"]
                + b["loc"]
                + a["mov"]
            )

            if new_sign in original_strings or new_sign in seen:
                continue

            if source_a_counts[row_a["gloss_id"]] >= 2:
                break

            seen.add(new_sign)
            source_a_counts[row_a["gloss_id"]] += 1

            candidates.append({
                "candidate_id": f"SS_A_{len(candidates)+1:03d}",
                "group": "SS",
                "combination": "A",
                "hf_source": row_a["gloss_id"],
                "hp_source": row_b["gloss_id"],
                "loc_source": row_b["gloss_id"],
                "mov_source": row_a["gloss_id"],
                "hf": a["hf"],
                "hp": b["hp"],
                "loc": b["loc"],
                "mov": a["mov"],
                "hamnosys": new_sign,
                "codepoints": to_codepoints(new_sign),
            })

            if len(candidates) >= 10:
                break

        if len(candidates) >= 10:
            break

    fields = [
        "candidate_id", "group", "combination",
        "hf_source", "hp_source", "loc_source", "mov_source",
        "hf", "hp", "loc", "mov", "hamnosys", "codepoints"
    ]

    with open(
        CANDIDATES_FILE, "w",
        encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(candidates)

    print(f"Generated SS-A candidates: {len(candidates)}")

    for c in candidates:
        print(
            f"{c['candidate_id']}: "
            f"HF/MOV={c['hf_source']}, "
            f"HP/LOC={c['hp_source']}"
        )
        print(f"  {c['codepoints']}")

    print(f"\nDiagnostics: {DIAGNOSTICS_FILE}")
    print(f"Candidates:  {CANDIDATES_FILE}")


if __name__ == "__main__":
    main()
