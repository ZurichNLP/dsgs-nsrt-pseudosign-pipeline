
"""Generate pilot SS candidates using the four source rules."""

import csv
import random
from pathlib import Path

from movement_extraction import (
    extract_complete_movement,
    to_codepoints,
)
from pilot_generation import eligible_source


ROOT = Path(__file__).resolve().parent

INPUT = (
    ROOT.parent
    / "step1_classification"
    / "output"
    / "analysis_ready_pool.csv"
)

OUTPUT = ROOT / "output" / "pilot_ss_abcd.csv"

TARGET_PER_CATEGORY = 10
MAX_ATTEMPTS = 30000
SEED = 42


def load_sources():
    """Load pilot-eligible SS signs."""

    with open(INPUT, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    original_strings = {row["hamnosys"] for row in rows}
    sources = []

    for row in rows:
        if (
            row["handshape_dsgs"] != "simple"
            or row["movement_class"] != "simple"
        ):
            continue

        extracted = extract_complete_movement(row["hamnosys"])

        if not eligible_source(row, extracted):
            continue

        sources.append({
            "id": row["gloss_id"],
            **extracted,
        })

    return sources, original_strings


def choose_sources(category, sources, rng):
    """Choose sources according to Sarah's requirements."""

    a, b = rng.sample(sources, 2)

    if category == "A":
        # HF/MOV from a; HP/LOC from b.
        return a, a, b, b

    if category == "B":
        # HF/MOV from a; HP and LOC from different signs.
        hp, loc = rng.sample(sources, 2)
        return a, a, hp, loc

    if category == "C":
        # HF and MOV from different signs; HP/LOC together.
        hp_loc = rng.choice(sources)
        return a, b, hp_loc, hp_loc

    if category == "D":
        # HF/MOV different; HP/LOC different.
        hp, loc = rng.sample(sources, 2)
        return a, b, hp, loc

    raise ValueError(f"Unknown category: {category}")


def check_sources(category, hf, mov, hp, loc):
    """Validate the four source relationships."""

    same_hf_mov = hf["id"] == mov["id"]
    same_hp_loc = hp["id"] == loc["id"]

    rules = {
        "A": (True, True),
        "B": (True, False),
        "C": (False, True),
        "D": (False, False),
    }

    if category not in rules:
        return False

    if (same_hf_mov, same_hp_loc) != rules[category]:
        return False

    # Exclude reconstructing all parameters from one source.
    if len({hf["id"], mov["id"], hp["id"], loc["id"]}) < 2:
        return False

    return True


def generate_category(category, sources, original_strings, rng):
    """Generate pilot candidates with source tracking."""

    candidates = []
    seen_provenance = set()

    for _ in range(MAX_ATTEMPTS):

        if len(candidates) >= TARGET_PER_CATEGORY:
            break

        hf, mov, hp, loc = choose_sources(
            category, sources, rng
        )

        if not check_sources(category, hf, mov, hp, loc):
            continue

        provenance = (
            hf["id"],
            mov["id"],
            hp["id"],
            loc["id"],
        )

        if provenance in seen_provenance:
            continue

        new_sign = (
            hf["hf"]
            + hp["hp"]
            + loc["loc"]
            + mov["mov"]
        )

        # Do not label an existing sign as a new candidate.
        if new_sign in original_strings:
            continue

        seen_provenance.add(provenance)

        candidates.append({
            "candidate_id": (
                f"SS_{category}_{len(candidates)+1:03d}"
            ),
            "group": "SS",
            "category": category,
            "hf_source": hf["id"],
            "mov_source": mov["id"],
            "hp_source": hp["id"],
            "loc_source": loc["id"],
            "hf": hf["hf"],
            "hp": hp["hp"],
            "loc": loc["loc"],
            "mov": mov["mov"],
            "hamnosys": new_sign,
            "codepoints": to_codepoints(new_sign),
            "source_check": "PASS",
        })

    return candidates


def validate_candidates(candidates, sources, original_strings):
    """Check the generated records against their sources."""

    source_by_id = {s["id"]: s for s in sources}

    for c in candidates:
        hf = source_by_id[c["hf_source"]]
        mov = source_by_id[c["mov_source"]]
        hp = source_by_id[c["hp_source"]]
        loc = source_by_id[c["loc_source"]]

        assert check_sources(c["category"], hf, mov, hp, loc)

        # Verify that each component was copied unchanged.
        assert c["hf"] == hf["hf"]
        assert c["mov"] == mov["mov"]
        assert c["hp"] == hp["hp"]
        assert c["loc"] == loc["loc"]

        assert c["hamnosys"] == (
            c["hf"] + c["hp"] + c["loc"] + c["mov"]
        )

        assert c["hamnosys"] not in original_strings


def main():
    sources, original_strings = load_sources()

    print(f"Pilot-eligible SS sources: {len(sources)}")

    if len(sources) < 2:
        raise ValueError("At least two source signs are required.")

    rng = random.Random(SEED)
    all_candidates = []

    for category in "ABCD":
        candidates = generate_category(
            category, sources, original_strings, rng
        )

        all_candidates.extend(candidates)

        print(
            f"Category {category}: "
            f"{len(candidates)}/{TARGET_PER_CATEGORY}"
        )

    validate_candidates(
        all_candidates, sources, original_strings
    )

    OUTPUT.parent.mkdir(exist_ok=True)

    fields = [
        "candidate_id", "group", "category",
        "hf_source", "mov_source",
        "hp_source", "loc_source",
        "hf", "hp", "loc", "mov",
        "hamnosys", "codepoints", "source_check"
    ]

    with open(
        OUTPUT, "w", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_candidates)

    unique_strings = len({
        c["hamnosys"] for c in all_candidates
    })

    print(f"\nTotal provenance records: {len(all_candidates)}")
    print(f"Unique generated strings: {unique_strings}")
    print("Source validation: PASS")
    print(f"Saved to: {OUTPUT}")

    print("\nSource examples:")

    for category in "ABCD":
        sample = next(
            (
                c for c in all_candidates
                if c["category"] == category
            ),
            None
        )

        if sample:
            print(
                f"{category}: "
                f"HF={sample['hf_source']}, "
                f"MOV={sample['mov_source']}, "
                f"HP={sample['hp_source']}, "
                f"LOC={sample['loc_source']}"
            )


if __name__ == "__main__":
    main()
