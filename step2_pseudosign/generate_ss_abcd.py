
"""Generate pilot SS candidates using the four source rules."""

import csv
import random
from pathlib import Path

from movement_extraction import (
    extract_complete_movement,
    balanced_brackets,
    to_codepoints,
)

ROOT = Path(__file__).resolve().parent

INPUT = ROOT / "output" / "source_parameters.csv" # provide extracted parameters

ORIGINAL_INPUT = (
    ROOT.parent
    / "step1_classification"
    / "output"
    / "analysis_ready_pool.csv"
)  # to check if generated candidates already exist in the original pool

# Choose one mode: "single", "sym_e0e9", "sym_e0e8", or "asym_two"
MODE = "asym_two"  # Change this to "single", "sym_e0e8", "sym_e0e9", or "asym_two" as needed


# These are always used in asym_two mode.
PLUS = chr(0xE0E7)
PAR_BEGIN = chr(0xE0E2)
PAR_END = chr(0xE0E3)

OUTPUT = ROOT / "output" / f"pilot_ss_{MODE}.csv"

TARGET_PER_CATEGORY = 10
MAX_ATTEMPTS = 30000
SEED = 42

def split_asym_blocks(text):
    """ Split at the only top-level E0E7"""

    depth = 0
    positions = []

    for i, char in enumerate(text):
        if char == PAR_BEGIN:
            depth += 1
        elif char == PAR_END:
            depth -= 1
            if depth < 0:
                return None
        elif char == PLUS and depth == 0:
            positions.append(i)

    if depth != 0 or len(positions) != 1:
        return None
    
    pos = positions[0]
    first = text[:pos]
    second = text[pos + 1:]

    if not first or not second:
        return None

    return first, second


def parse_asym_source(text):
    """ Parse and reconstruct two blocks of an asymmetric sign"""

    blocks = split_asym_blocks(text)

    if blocks is None:
        return None
    
    first_text, second_text = blocks

    first = extract_complete_movement(
        first_text, allow_empty_movement=True
    )

    second = extract_complete_movement(
        second_text, allow_empty_movement=True
    )

    if first is None or second is None:
        return None
    
    # Both blocks need HF, HP, and a movement-containing suffix.
    for part in (first, second):
        if not part["hf"] or not part["hp"]:
            return None
        
    if not first["mov"] or not second["mov"]:
        return None
    
    def rebuild(part):
        return (
            part["symmetry"]
            + part["hf"]
            + part["hp"]
            + part["loc"]
            + part["mov"]
        )
    
    if rebuild(first) + PLUS + rebuild(second) != text:
        return None
    
    return first, second


def load_sources():
    """Load extracted SS parameters and original sign strings"""

    with open(INPUT, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    sources = []
    ss_count = 0

    for row in rows:
        if row["group"] != "SS":
            continue

        ss_count += 1

        if MODE == "single":
            if row["handedness"] != "single" or row["symmetry"] != "":
                continue

        elif MODE in ("sym_e0e9", "sym_e0e8"):
            expected_symmetry = (
                chr(0xE0E9) if MODE == "sym_e0e9" 
                else chr(0xE0E8)
            )
            if (
                row["handedness"] != "sym_two"
                or row["symmetry"] != expected_symmetry
            ):
                continue

        elif MODE == "asym_two":
            if row["handedness"] != "asym_two":
                continue
            
        else:
            raise ValueError(f"Unknown mode: {MODE}")


        if not balanced_brackets(row["hamnosys"]):
            continue

        if MODE == "asym_two":
            parsed = parse_asym_source(row["hamnosys"])

            if parsed is None:
                continue

            first, second = parsed

            sources.append({
                "id": row["gloss_id"],
                "symmetry": first["symmetry"],
                "hf": first["hf"],
                "hp": first["hp"],
                "loc": first["loc"],
                "mov": first["mov"],
                "second": second,  # second is nested dictionary containing the second block's parameters
            })
        else:
            if not row["hf"] or not row["hp"] or not row["mov"]:
                continue

            sources.append({
                "id": row["gloss_id"],
                "symmetry": row["symmetry"],
                "hf": row["hf"],
                "hp": row["hp"],
                "loc": row["loc"],
                "mov": row["mov"],
            })

    with open(ORIGINAL_INPUT, encoding="utf-8-sig", newline="") as f:
        original_rows = csv.DictReader(f)
        original_strings = {
            row["hamnosys"] for row in original_rows
        }

    print(f"Extracted SS records: {ss_count}")

    """
    from collections import Counter

    ss_rows = [row for row in rows if row["group"] == "SS"]

    excluded = [
        row for row in ss_rows
        if row["gloss_id"] not in {s["id"] for s in sources}
    ]

    print("\nExcluded SS by handedness:")
    print(Counter(row["handedness"] for row in excluded))

    print("\nReasons for exclusion:")
    print("Not single:", sum(
        row["handedness"] != "single" for row in excluded
    ))
    print("Has symmetry:", sum(
        bool(row["symmetry"]) for row in excluded
    ))
    print("Has E0E7:", sum(
        chr(0xE0E7) in row["hamnosys"] for row in excluded
    ))
    print("Missing HF/HP/MOV:", sum(
        not row["hf"] or not row["hp"] or not row["mov"]
        for row in excluded
    ))
    print("Unbalanced brackets:", sum(
        not balanced_brackets(row["hamnosys"])
        for row in excluded
    ))
    """

    if MODE == "asym_two":
        print(f"Asymmetric sources accepted: {len(sources)}/54")
        print(f"Asymmetric sources excluded: {54 - len(sources)}")

    loc_sources = [s for s in sources if s["loc"]]

    return sources, loc_sources, original_strings

    """
    After running: 

    Extracted SS records: 785

    Excluded SS by handedness:
    Counter({'sym_two': 312, 'asym_two': 54})

    Reasons for exclusion:
    Not single: 366
    Has symmetry: 312
    Has E0E7: 96
    Missing HF/HP/MOV: 0
    Unbalanced brackets: 0

    my next step is to process two-handed SS signs.
    """


def choose_sources(category, sources, loc_sources, rng):
    """Choose HF, MOV, HP, LOC sources for A/B/C/D categories."""

    if not loc_sources:
        raise ValueError("No sources with explicit LOC")

    a, b = rng.sample(sources, 2)

    if category == "A":
        # HF/MOV same; HP/LOC same.
        hp_loc = rng.choice(loc_sources) # I use loc_sources when choosing hp_loc to ensure that the chosen source has a real(non-empty) location.
        return a, a, hp_loc, hp_loc

    if category == "B":
        # HF/MOV same; HP/LOC different.
        hp = rng.choice(sources)
        loc = rng.choice(loc_sources)
        return a, a, hp, loc

    if category == "C":
        # HF/MOV different; HP/LOC same.
        hp_loc = rng.choice(loc_sources)
        return a, b, hp_loc, hp_loc

    if category == "D":
        # HF/MOV different; HP/LOC different.
        """Since I understand the rule as: HF_source != MOV_source AND HP_source != LOC_source. 
        This doesn't mean four sources must be different, but at least two sources must be different. """

        hp = rng.choice(sources)
        loc = rng.choice(loc_sources)
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

    if category not in rules: # This should not happen, but just in case.
        return False

    if (same_hf_mov, same_hp_loc) != rules[category]: # Check if the source relationships match the category rules.
        return False

    # Exclude reconstructing all parameters from one source.
    if len({hf["id"], mov["id"], hp["id"], loc["id"]}) < 2: # automated check if there are at least two different sources in the set.
        return False

    return True


def check_candidate(new_sign, hf, mov, hp, loc):
    """Check whether the generated parameters can be recovered"""

    if not balanced_brackets(new_sign):
        return False
    
    if MODE == "asym_two":
        parsed = parse_asym_source(new_sign)

        if parsed is None:
            return False
        
        first, second = parsed

        # Check block 1
        first_ok = (
            first["symmetry"] == mov["symmetry"]
            and first["hf"] == hf["hf"]
            and first["hp"] == hp["hp"]
            and first["loc"] == loc["loc"]
            and first["mov"] == mov["mov"]
        )

        # Check block 2
        second_ok = (
            second["symmetry"] == mov["second"]["symmetry"]
            and second["hf"] == hf["second"]["hf"]
            and second["hp"] == hp["second"]["hp"]
            and second["loc"] == loc["second"]["loc"]
            and second["mov"] == mov["second"]["mov"]
        )

        return first_ok and second_ok
    
    result = extract_complete_movement(new_sign)

    if result is None:
        return False
    
    return(
        result["symmetry"] == mov["symmetry"]
        and result["hf"] == hf["hf"]
        and result["hp"] == hp["hp"]
        and result["loc"] == loc["loc"]
        and result["mov"] == mov["mov"]
    )




def generate_category(category, sources, loc_sources, original_strings, rng):
    """Generate pilot candidates with source tracking."""

    candidates = []
    seen_provenance = set()

    for _ in range(MAX_ATTEMPTS):

        if len(candidates) >= TARGET_PER_CATEGORY:
            break

        hf, mov, hp, loc = choose_sources(
            category, sources, loc_sources, rng
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
        
        symmetry = mov["symmetry"]

        # Build the first block.
        first_block = (
            symmetry
            + hf["hf"]
            + hp["hp"]
            + loc["loc"]
            + mov["mov"]
        )
        
        # Default values for single and symmetric signs.
        second_symmetry = ""
        second_hf = ""
        second_hp = ""
        second_loc = ""
        second_mov = ""

        if MODE == "asym_two":
            # Select the second block's parameters from the "second" field of the mov, hf, hp, and loc dictionaries.
            second_symmetry = mov["second"]["symmetry"]
            second_hf = hf["second"]["hf"]
            second_hp = hp["second"]["hp"]
            second_loc = loc["second"]["loc"]
            second_mov = mov["second"]["mov"]

            second_block = (
                second_symmetry
                + second_hf
                + second_hp
                + second_loc
                + second_mov
            )

            new_sign = first_block + PLUS + second_block

        else:
            new_sign = first_block

        # Do not label an existing sign as a new candidate.
        if new_sign in original_strings:
            continue

        if not check_candidate(new_sign, hf, mov, hp, loc):
            continue

        seen_provenance.add(provenance)

        candidates.append({
            "candidate_id": (
                f"SS_{MODE}_{category}_{len(candidates)+1:03d}"
            ),
            "group": "SS",
            "category": category,

            "hf_source": hf["id"],
            "mov_source": mov["id"],
            "hp_source": hp["id"],
            "loc_source": loc["id"],

            # First block
            "symmetry": symmetry,
            "hf": hf["hf"],
            "hp": hp["hp"],
            "loc": loc["loc"],
            "mov": mov["mov"],

            # Second block (only for asym_two, empty for others)
            "symmetry2": second_symmetry,
            "hf2": second_hf,
            "hp2": second_hp,
            "loc2": second_loc,
            "mov2": second_mov,

            "hamnosys": new_sign,
            "codepoints": to_codepoints(new_sign),
            "source_check": "PASS",
        })

    return candidates


def validate_candidates(candidates, sources, original_strings):
    """Check the generated records against their sources."""

    source_by_id = {s["id"]: s for s in sources}

    for candidate in candidates:
        hf = source_by_id[candidate["hf_source"]]
        mov = source_by_id[candidate["mov_source"]]
        hp = source_by_id[candidate["hp_source"]]
        loc = source_by_id[candidate["loc_source"]]

        assert check_sources(candidate["category"], hf, mov, hp, loc)

        # First block.
        assert candidate["symmetry"] == mov["symmetry"]
        assert candidate["hf"] == hf["hf"]
        assert candidate["hp"] == hp["hp"]
        assert candidate["loc"] == loc["loc"]
        assert candidate["mov"] == mov["mov"]

        first_block = (
            candidate["symmetry"]
            + candidate["hf"] 
            + candidate["hp"] 
            + candidate["loc"] 
            + candidate["mov"]
        )

        if MODE == "asym_two":
            # Second block.
            assert candidate["symmetry2"] == mov["second"]["symmetry"]
            assert candidate["hf2"] == hf["second"]["hf"]
            assert candidate["hp2"] == hp["second"]["hp"]
            assert candidate["loc2"] == loc["second"]["loc"]
            assert candidate["mov2"] == mov["second"]["mov"]

            second_block = (
                candidate["symmetry2"]
                + candidate["hf2"] 
                + candidate["hp2"] 
                + candidate["loc2"] 
                + candidate["mov2"]
            )

            expected_sign = first_block + PLUS + second_block

        else:
            expected_sign = first_block

        assert candidate["hamnosys"] == expected_sign
        
        assert check_candidate(
            candidate["hamnosys"], hf, mov, hp, loc
        )

        assert candidate["hamnosys"] not in original_strings


def main():
    sources, loc_sources, original_strings = load_sources()

    print(f"Pilot-eligible SS sources: {len(sources)}")

    if len(sources) < 2:
        raise ValueError("At least two source signs are required.")

    rng = random.Random(SEED)
    all_candidates = []

    for category in "ABCD":
        candidates = generate_category(
            category, sources, loc_sources, original_strings, rng
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

        "symmetry", "hf", "hp", "loc", "mov",
        "symmetry2", "hf2", "hp2", "loc2", "mov2",

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
