
"""Extract HamNoSys parameters and audit their boundaries."""

import csv
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PARSER_DIR = SCRIPT_DIR / "hamparse_py3"
sys.path.insert(0, str(PARSER_DIR))

from handform import getHandform
from handposition import getHandposition
from location import getLocation
from movement import getMovement


BETWEEN = chr(0xE0E6)
REPETITIONS = "[" + "".join(chr(cp) for cp in range(0xE0D8, 0xE0DD)) + "]"
CONTACT = "[" + "".join(chr(cp) for cp in range(0xE0D0, 0xE0D7)) + "]"
SIZES = "[" + chr(0xE0C6) + chr(0xE0C7) + "]"
SPEEDS = "[" + chr(0xE0C8) + chr(0xE0C9) + "]"
ALTERNATING = chr(0xE0DD)

SYMMETRY_OPS = {0xE0E8, 0xE0E9}
ASYM_SEPARATOR = 0xE0E7
OPEN_BRACKET = 0xE0E2
CLOSE_BRACKET = 0xE0E3
REPLACEMENT = 0xE0AA

INPUT_FILE = (
    SCRIPT_DIR.parent
    / "step1_classification/output/analysis_ready_pool.csv"
)
OUTPUT_DIR = SCRIPT_DIR / "output"


def prefix_match(matches, text):
    """Return the longest match anchored at position zero."""
    valid = [m for m in matches if m and text.startswith(m)]
    return max(valid, key=len) if valid else None

def probe_structural_prefix(matches_fn, text):
    """Probe parameters after one structural marker, without removing it."""
    if not text:
        return None

    markers = {0xE0E2, 0xE0DD}

    if ord(text[0]) not in markers:
        return None

    inner = text[1:]
    match = prefix_match(matches_fn(inner), inner)

    if not match:
        return None

    return {
        "marker": text[0],
        "parameter": match,
        "remaining": inner[len(match):],
    }

def _extract_with_reason(hamnosys, allow_empty_movement=False):
    """Extract parameters and report the first extraction failure."""
    if not hamnosys:
        return None, "empty_hamnosys"

    remaining = hamnosys
    symmetry = ""

    if ord(remaining[0]) in SYMMETRY_OPS:
        symmetry = remaining[0]
        remaining = remaining[1:]

    try:
        hf = prefix_match(
            getHandform(remaining, BETWEEN, REPETITIONS),
            remaining,
        )
        if not hf:
            probe = probe_structural_prefix(
                lambda text: getHandform(text, BETWEEN, REPETITIONS),
                remaining,
            )
            if probe:
                return None, "hf_structural_prefix_candidate"
            return None, "hf_not_found"
        
        remaining = remaining[len(hf):]

        hp = prefix_match(
            getHandposition(
                remaining, BETWEEN, REPETITIONS,
                CONTACT, ALTERNATING, SPEEDS,
            ),
            remaining,
        )
        if not hp:
            probe = probe_structural_prefix(
                lambda text: getHandposition(
                    text, BETWEEN, REPETITIONS,
                    CONTACT, ALTERNATING, SPEEDS
                ),
                remaining,
            )
            if probe:
                return None, "hp_structural_prefix_candidate"
            return None, "hp_not_found"
        
        remaining = remaining[len(hp):]

        loc = prefix_match(
            getLocation(
                remaining, BETWEEN, CONTACT, REPETITIONS
            ),
            remaining,
        )
        loc = loc or ""
        remaining = remaining[len(loc):]

        mov = remaining

        if not mov:
            if allow_empty_movement:
                parser_matches = []

            else:
                return None, "empty_mov"   

        else:
            parser_matches = getMovement(
                mov, BETWEEN, SIZES, SPEEDS, REPETITIONS, CONTACT
            )

            if not parser_matches:
                return None, "mov_not_recognised"

    except Exception as exc:
        return None, f"parser_error:{type(exc).__name__}"

    result = {
        "symmetry": symmetry,
        "hf": hf,
        "hp": hp,
        "loc": loc,
        "mov": mov,
        "parser_matches": parser_matches,
    }

    if symmetry + hf + hp + loc + mov != hamnosys:
        return None, "reconstruction_failed"

    return result, ""
    """limitation here: This can only garantee there is no character lost, 
    it cannot garantee the parser matches/parameter borders are correct."""



def extract_complete_movement(hamnosys, allow_empty_movement=False):
    """Extract parameters, optionally allowing a static block."""

    result, _ = _extract_with_reason(
        hamnosys,
        allow_empty_movement=allow_empty_movement,
    )
    return result


def balanced_brackets(text):
    """Check structural E0E2/E0E3 bracket pairing."""
    depth = 0

    for char in text:
        cp = ord(char)

        if cp == OPEN_BRACKET:
            depth += 1
        elif cp == CLOSE_BRACKET:
            depth -= 1

        if depth < 0:
            return False

    return depth == 0 # True if all brackets are closed.



def audit_source(hamnosys, handedness=""):
    """Extract parameters and retain structural information."""

    result, failure = _extract_with_reason(hamnosys)

    if result is None:
        return {
            "status": "unresolved",
            "reason": failure,
        }
    
    mov = result["mov"]

    # Check bracket pairing in the complete transcription.
    if not balanced_brackets(hamnosys):
        return {
            "status": "unresolved",
            "reason": "unbalanced_brackets",
        }

    return {
        **result,
        "status": "extracted",
        "reason": "",
        "handedness": handedness,
        "has_location": bool(result["loc"]),
        "has_replacement": any(
            ord(ch) == REPLACEMENT for ch in mov
        ),
        "has_movement_brackets": any(
            ord(ch) == OPEN_BRACKET for ch in mov
        ),
        "has_separator_in_suffix": any(
            ord(ch) == ASYM_SEPARATOR for ch in mov
        ),
    }


def to_codepoints(text):
    """Convert HamNoSys symbols to readable codepoints."""
    return " ".join(f"E{ord(ch)-0xE000:03X}" for ch in text)


def run_corpus_audit():
    """Audit the full corpus and write parameter/review tables."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with INPUT_FILE.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    extracted_rows = []
    failed_rows = []
    statuses = Counter()
    reasons = Counter()
    groups = Counter()

    for row in rows:
        result = audit_source(
            row["hamnosys"],
            row.get("handedness", ""),
        )

        status = result["status"]
        reason = result["reason"]

        statuses[status] += 1

        if reason:
            for flag in reason.split(";"):
                reasons[flag] += 1

        group = (
            row["handshape_dsgs"][0].upper()
            + row["movement_class"][0].upper()
        )
        groups[(group, status)] += 1

        record = {
            "gloss_id": row["gloss_id"],
            "group": group,
            "handedness": row.get("handedness", ""),
            "status": status,
            "reason": reason,
            "hamnosys": row["hamnosys"],
        }

        if status == "extracted":
            record.update({
                "symmetry": result["symmetry"],
                "hf": result["hf"],
                "hp": result["hp"],
                "loc": result["loc"],
                "mov": result["mov"],
                "mov_codepoints": to_codepoints(result["mov"]),
                "has_location": result["has_location"],
                "has_replacement": result["has_replacement"],
                "has_movement_brackets": result["has_movement_brackets"],
                "has_separator_in_suffix": result["has_separator_in_suffix"],
            })
            extracted_rows.append(record)

        else:
            failed_rows.append(record)

    def write_csv(path, data, fields):
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, restval="")
            writer.writeheader()
            writer.writerows(data)

    source_fields = [
        "gloss_id", "group", "handedness", "status", "reason",
        "hamnosys", "symmetry", "hf", "hp", "loc", "mov",
        "mov_codepoints", "has_location", "has_replacement",
        "has_movement_brackets", "has_separator_in_suffix",
    ]
    failed_fields = [
        "gloss_id", "group", "handedness", "status", "reason",
        "hamnosys",
    ]

    write_csv(
        OUTPUT_DIR / "source_parameters.csv",
        extracted_rows,
        source_fields,
    )
    write_csv(
        OUTPUT_DIR / "extraction_review.csv",
        failed_rows,
        failed_fields,
    )

    print(f"Total signs: {len(rows)}")
    print("\nExtraction status:")
    for status, count in statuses.most_common():
        print(f"  {status}: {count}")

    print("\nGroup breakdown:")
    for group in ("SS", "SC", "CS", "CC"):
        print(
            f"  {group}: "
            f"extracted={groups[(group, 'extracted')]}, "
            f"unresolved={groups[(group, 'unresolved')]}"
        )

    print("\nReasons and structural flags:")
    for reason, count in reasons.most_common():
        print(f"  {reason}: {count}")

    print("\nSaved:")
    print(OUTPUT_DIR / "source_parameters.csv")
    print(OUTPUT_DIR / "extraction_review.csv")


if __name__ == "__main__":
    run_corpus_audit()
