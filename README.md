## Project Overview

Master's thesis: developing a Swiss German Sign Language (DSGS) version of the Nonsense Sign Repetition Task (NSRT), based on the [BSL NSRT (Mann & Marshall,2010)](https://signlang-assessment.info/nonsense-sign-repetition-task-for-british-sign-language.html).

### Pipeline

**Step 1 — Classify DSGS signs by complexity (HamNoSys-based)**
Identify DSGS signs with low and high complexity along two dimensions — handshape and movement — using HamNoSys notations.

|                                             |    Simple handshape (unmarked) |    Complex handshape (marked) |
|---------------------------------------------|--------------------------------|-------------------------------|
| **Simple movement** (path OR hand-internal) | Level 0: 10 items              | Level 1b: 10 items            |
| **Complex movement** (path + hand-internal) | Level 1a: 10 items             | Level 2: 10 items             |


The authors of this test manipulated the phonetic complexity of nonsense signs along two phonological parameters: handshape and movement. For each parameter, items were either phonetically “simple” or phonetically “complex” (Table 1). With respect to handshape,  “simple” handshapes were the four unmarked handshapes, labeled here as “B”, “5”, “G”, and “A” (Sutton-Spence & Woll, 1999) and “complex” handshapes were all marked handshapes. With respect to movement, the authors defined just one movement, whether internal or path, as “simple”, and two movements (i.e., internal and path combined) as “complex”.


**Step 2 — Define new signs**
Define new (non-)signs consisting of the handshapes and movements identified on the basis of HamNoSys

**Step 3 — Create poses**
Create the poses for those new (non-)signs based on [Arkushin et al. (2023)](https://rotem-shalev.github.io/ham-to-pose/) (paper and code linked at the top)

**Step 4 (optional) — Video synthesis**
Use the poses as input for a sign language production process to synthesize videos of digital signers.
