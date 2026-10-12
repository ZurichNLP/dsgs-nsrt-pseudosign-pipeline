"""
HamNoSys classification dictionaries for DSGS handshape / movement analysis.

Base data: extracted from Schulder & Hanke (2022) hamnosys.dtx v1.0.3
           (CTAN, DOI 10.25592/uhhfdm.9901) via hamnosys_parser.py.
           209 symbols total, verbatim from LaTeX source.

Sub-categorization sources:
  - HamNoSys 4.0 User Guide (Robert Smith 2013)
  - Mann et al. (2010) operational simple/complex definitions
  - Battison (1978) unmarked handshape inventory
  - Sutton-Spence & Woll (1999) BSL 4 selection
  - Boyes Braem (1995) DSGS Grundhandformen (6)

"""

from hamnosys_parser import parse_dtx

#  BASE CODEPOINT -> NAME MAPPING (verbatim from .dtx)

CODEPOINT_TO_NAME = {}   # {codepoint: symbol_name}
NAME_TO_CODEPOINT = {}   # {symbol_name: codepoint}
SECTIONS = {}            # {section_name: [codepoints]}


def _init():
    """Populate the base mappings from the .dtx source."""
    secs = parse_dtx()
    for sec_name, pairs in secs.items():
        SECTIONS[sec_name] = [cp for _, cp in pairs]
        for name, cp in pairs:
            CODEPOINT_TO_NAME[cp] = name
            NAME_TO_CODEPOINT[name] = cp


_init()  # Run once when module is imported


# ---- HANDSHAPES ----

# Two levels of categorization apply here, and they mean different things:
#
# 1. Hanke's transcription categorization (from .dtx source):
#    HamNoSys uses 12 "base handshape" building blocks (U+E000-U+E00B) plus 8 modifiers (U+E00C-U+E014). 
#    Handshapes are transcribed as one base + zero or more modifiers.
#    This is the toolkit level, not a phonological judgment.
#
# 2. Phonological simple/complex distinction (from Battison tradition):
#    A subset of these 12 base handshapes counts as "unmarked" / "simple" for a given sign language. 
#
#   For BSL: Sutton-Spence & Woll (1999) identified 4 unmarked handshapes,
#            adopted operationally by Mann et al. (2010).
#   For DSGS: Boyes Braem (1995) identified 6 Grundhandformen.
#   The BSL 4 is a strict subset of the DSGS 6.



# --- All 12 base handshapes from Schulder & Hanke (2022) .dtx §Handshapes ---
# These are the raw transcription building blocks, not a phonological judgment.
BASE_HANDSHAPES = set(SECTIONS['Handshapes'])
# Contents (.dtx name / [Palette equivalent] / handshape label):
#   U+E000  hamfist                                            -> A (fist)
#   U+E001  hamflathand                                        -> B (flat, fingers together)
#   U+E002  hamfingertwo   [hamfinger2]                        -> G / "1" (index extended)
#   U+E003  hamfingertwothree  [hamfinger23]                
#   U+E004  hamfingertwothreespread    [hamfinger23spread]   
#   U+E005  hamfingertwothreefourfive   [hamfinger2345]        -> 5 (five fingers)
#   U+E006  hampinchonetwo    [hampinch12]                  
#   U+E007  hampinchall                                        -> O (all fingers touch thumb)
#   U+E008  hampinchonetwoopen  [hampinch12open]            
#   U+E009  hamceeonetwo      [hamcee12]                      
#   U+E00A  hamceeall                                          -> C (all fingers curved)
#   U+E00B  hamceeopen                                         


# --- Handshape modifiers (8 from Schulder & Hanke (2022) .dtx §Handshape modifiers) ---
# Tolerated in the handshape slot; do not indicate a different base handshape.
# Includes thumb position, finger bending, hook shape, etc.
HANDSHAPE_MODIFIERS = set(SECTIONS['Handshape modifiers'])


# --- Handshape labels used in our classification ---

# Confidence key:
#   [HIGH]      = Symbol name and visual are unambiguous
#   [CONFIRMED] = Verified via HamNoSys Palette

HANDSHAPE_LABEL_TO_CODEPOINT = {
    'A': 0xE000,  # hamfist                        [HIGH]
    'B': 0xE001,  # hamflathand                    [HIGH]
    'G': 0xE002,  # hamfingertwo (aka "1")         [HIGH]
    '5': 0xE005,  # hamfingertwothreefourfive      [CONFIRMED via Palette]
    'C': 0xE00A,  # hamceeall                      [HIGH]
    'O': 0xE007,  # hampinchall                    [CONFIRMED via Palette and Sarah]
}



# --- SIMPLE (unmarked) HANDSHAPE SETS FOR CLASSIFICATION ---
#
# simple/unmarked  = the sign's dominant base handshape is IN this set
# complex/marked = the sign's dominant base handshape is NOT in this set

# Sutton-Spence & Woll (1999) BSL 4, as adopted by Mann et al. (2010)

SIMPLE_HANDSHAPES_BSL4 = {
    HANDSHAPE_LABEL_TO_CODEPOINT['A'],   # U+E000  hamfist
    HANDSHAPE_LABEL_TO_CODEPOINT['B'],   # U+E001  hamflathand
    HANDSHAPE_LABEL_TO_CODEPOINT['G'],   # U+E002  hamfingertwo
    HANDSHAPE_LABEL_TO_CODEPOINT['5'],   # U+E005  hamfingertwothreefourfive
}

# Boyes Braem (1995) DSGS 6 Grundhandformen
# Rationale: The BSL 4 plus C and O, based on DSGS-specific early acquisition
# data (Boyes Braem 1995) AND cross-linguistic universality (Battison 1978).
# BSL 4 is a strict subset of DSGS 6.
SIMPLE_HANDSHAPES_DSGS6 = SIMPLE_HANDSHAPES_BSL4 | {
    HANDSHAPE_LABEL_TO_CODEPOINT['C'],   # U+E00A  hamceeall
    HANDSHAPE_LABEL_TO_CODEPOINT['O'],   # U+E007  hampinchall
}
# NOTE on Boyes Braem (1995, 3rd ed.) Fig.Abb.IX-I, p. 173: The handshape ICONS for 
# F and O are reversed in the book, but the letter labels and HamNoSys symbols next 
# to them are correct and match Hanke's HamNoSys 4 Handshapes Chart. The DSGS "O" 
# handshape is encoded as hampinchall (E007), i.e., all fingers touching thumb.
# Confirmed by Sarah.


# --- Sanity: DSGS 6 must contain BSL 4 ---
assert SIMPLE_HANDSHAPES_BSL4.issubset(SIMPLE_HANDSHAPES_DSGS6), \
    "BSL 4 should be a strict subset of DSGS 6"





# ---- MOVEMENT sub-categorization (77 symbols in .dtx §Movement) ----

# HamNoSys guide §7.1 = "hand movements in space" = PM (path movement)
# HamNoSys guide §7.2 = "hand movements without changing location" = IM (internal)

# Mann et al. (2010) defines movement complexity operationally:
#   - simple  = one movement (either PM or IM alone)
#   - complex = two movements simultaneously (PM + IM co-temporal)

# --- PM: Path Movement (hand travels through space) ---
# The definition of PM (path movement) follows HamNoSys 4.0 User Guide §7.1:
# any movement of the hand through space, including:
#   §7.1.1 Straight movements
#   §7.1.2 Curved / arc movements
#   §7.1.4 Wavy and zigzag movements
#   §7.1.5 Circular movements
#   §7.1.6 Elliptical movements
# All these subcategories are treated as PM in our classification.


# Straight arrows in 18 directions    # (Guide §7.1.1)
PM_STRAIGHT = set(range(0xE080, 0xE092))     # U+E080-U+E091

# Circular movements in 18 orientations (Guide §7.1.5)
PM_CIRCULAR = set(range(0xE092, 0xE0A4))     # U+E092-U+E0A3

# Primary PM symbols (initiate a path movement)
PM_PRIMARY = PM_STRAIGHT | PM_CIRCULAR

# PM modifiers (attach to a PM symbol; still contribute to "path")
# These typically co-occur with PM_PRIMARY symbols to describe the exact
# path shape (arc direction, wavy modulation, ellipse axis, spiral, 
# start/end position of a circle). The HamNoSys 4.0 User Guide (Smith 2013)
# §7.1.2, 7.1.4, 7.1.5, 7.1.6 describes their usage in combination with
# primary movements, but does not explicitly prohibit standalone use.

PM_MODIFIERS = (
    set(range(0xE0B0, 0xE0B9))             # clock positions (start/end of circle) （Guide §7.1.5)
    | {0xE0B9, 0xE0BA, 0xE0BB, 0xE0BC}     # arc directions (Guide §7.1.2)
    | {0xE0BD, 0xE0BE}                     # wavy, zigzag (Guide §7.1.4)
    | set(range(0xE0C0, 0xE0C4))           # ellipse axes (Guide §7.1.6)
    | {0xE0C4, 0xE0C5}                     # spiral increasing/decreasing
)

# Union: any codepoint that indicates "path movement is happening"
PM_ALL = PM_PRIMARY | PM_MODIFIERS


# --- IM: Internal Movement (hand does not change location) ---
# Guide §7.2 lists three sub-types:
#   - Changes in shape or orientation of the hand
#   - Wrist movements (up-down, left-right, rotation)
#   - Finger movements (fingerplay / wiggling)

IM_SHAPE_CHANGE = {
    0xE0AA,  # hamreplace — handshape/orientation change (↦ arrow)
}

IM_WRIST = {
    0xE0A5,  # hamnodding    — wrist up-down
    0xE0A6,  # hamswinging   — wrist left-right
    0xE0A7,  # hamtwisting   — wrist rotation
}

IM_FINGERS = {
    0xE0A4,  # hamfingerplay — finger wiggling
}

# Additional codepoints in the U+E0A4-U+E0AA range whose §7.1 vs §7.2
# assignment is not explicitly stated in the Guide. Position (clustered
# with IM symbols) and semantics ("stir" = compact circular action) 
# suggest IM.

IM_INFERRED = {
    0xE0A8,  # hamstircw   — stir clockwise
    0xE0A9,  # hamstirccw  — stir counter-clockwise
}

# Union: any codepoint we treat as IM in classification
IM_ALL = IM_SHAPE_CHANGE | IM_WRIST | IM_FINGERS | IM_INFERRED

# --- Movement segment NEUTRAL modifiers (do NOT count as PM or IM) ---
# These codepoints all sit in Hanke's HamNoSys inventory §Movement section, 
# but functionally they describe distance, contact, or spatial configuration, not the movement type itself.


STATIC_MARKER = {0xE0AF}  # hamnomotion - explicit "no motion"

MODALITY = {              # Guide §7.4 - speed/tension modifiers
    0xE0C8,  # hamfast
    0xE0C9,  # hamslow
    0xE0CA,  # hamtense
    0xE0CB,  # hamrest
    0xE0CC,  # hamhalt
}

CONTACT = {               # contact modifiers (Guide §Location and §Movements)
    0xE0D0,  # hamclose
    0xE0D1,  # hamtouch
    0xE0D2,  # haminterlock
    0xE0D3,  # hamcross
    0xE0D4,  # hamarmextended
    0xE0D5,  # hambehind
    0xE0D6,  # hambrushing
}

# From .dtx §Movement modifiers
SIZE_MODIFIERS = set(SECTIONS['Movement modifiers'])
# Contents: hamsmallmod (E0C6), hamlargemod (E0C7)


# ---- STRUCTURAL SYMBOLS (from .dtx §Other symbols) ----

# Classification logic only needs to detect co-temporal brackets
# (Mann's cluster marker for complex movement). All other structural
# codepoints are "skip", because they do not affect PM/IM judgment.

# Guide §7.8 "Combination of actions" defines three combination types:
#   Sequential:  Action1 Action2     
#   Co-temporal: [ Action1 Action2 ]     ← MANN'S CLUSTER = complex
#   Fusion:      < Action1 Action2 >

COTEMPORAL_OPEN  = 0xE0E2  # hamparbegin  [
COTEMPORAL_CLOSE = 0xE0E3  # hamparend    ]


# Symmetry operators (mark start of two-handed signs)

# When a HamNoSys string begins with one of these, the sign is two-handed.
# The parser skips the symmetry operator and starts reading the dominant
# hand's handshape from the next codepoint.

SYMMETRY_OPS = {
    0xE0E8,  # hamsymmpar  - parallel symmetry
    0xE0E9,  # hamsymmlr   - left-right (mirror) symmetry
}


# Dominant-vs-non-dominant separator in non-symmetric two-handed signs.
# Guide §9: structure is [dominant_hand ≠ non-dominant_hand], where ≠ is
# rendered by hamplus (E0E7).
# In classification we analyze only the dominant hand (Battison's Dominance constraint;
# Mann 2010 dominant-hand phonology).
ASYM_SEPARATOR = 0xE0E7  # hamplus (≠)


# Non-dominant hand static marker (Guide §9.2 Mixed Case)
# Standard use: at sign start, "instead of symmetry symbol" (§9.2 Bullet 3 "without"). 
# 5 DSGS signs use it mid-sign after ASYM_SEPARATOR.
NON_DOMINANT_MARKER = 0xE0EA  # hamnondominant

# All other §Other symbols codepoints — declared as "skip"
# Derived by subtracting the codepoints classification actually uses from the full §Other symbols section. 
# This ensures: Sanity check confirms complete coverage of §Other symbols (no "unclassified" warnings during runs)
# Contents include:
#   - Sequential brackets
#   - Fusion brackets
#   - Repetition markers
#   - Meta symbols

SKIP_STRUCTURAL = (
    set(SECTIONS['Other symbols'])
    - {COTEMPORAL_OPEN, COTEMPORAL_CLOSE}
    - SYMMETRY_OPS
    - {NON_DOMINANT_MARKER}
    - {ASYM_SEPARATOR}
)

# --- Sanity check: verify §Other symbols is fully covered ---
_all_other = set(SECTIONS['Other symbols'])
_used_other = (
    {COTEMPORAL_OPEN, COTEMPORAL_CLOSE}
    | SYMMETRY_OPS
    | {NON_DOMINANT_MARKER}
    | {ASYM_SEPARATOR}
    | SKIP_STRUCTURAL
)
assert _all_other == _used_other, \
    f"§Other symbols coverage mismatch: {_all_other ^ _used_other}"

# --- Sanity check: verify §Movement is fully covered ---
if 'Movement' in SECTIONS:
    _all_movements = set(SECTIONS['Movement'])
    _used_movements = PM_ALL | IM_ALL | STATIC_MARKER | MODALITY | CONTACT
    
    assert _all_movements == _used_movements, \
        f"§Movement mismatch: {_all_movements ^ _used_movements}"

# --- Sanity check: Disjoint movement categories ---
assert len(PM_ALL & IM_ALL) == 0, \
    f"PM & IM Conflict: {PM_ALL & IM_ALL}"
