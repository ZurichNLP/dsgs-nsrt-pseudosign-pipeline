# CC Generation – Notes for Future Work

## 1. Current Status

The DSGS corpus has been classified using the DSGS-6 handshape inventory and movement complexity criteria.

- SS: 1,103 signs
- SC: 795 signs
- CS: 243 signs
- CC: 178 signs

CC refers to signs with **complex handshapes and complex movements**.

The initial parameter extraction returned results for 167 out of 178 CC signs. However, these results have not all been validated.

## 2. Main Challenges

CC signs often contain more complicated HamNoSys structures, including:

- **Parallel movements:** Multiple movement components represented together using brackets.
- **Replacement (`E0AA`):** Changes in handshape or position within a movement.
- **Nested structures:** Brackets and movement components appearing within other structures.
- **Parameter boundaries:** Difficulty separating initial HF, HP, LOC, and complete MOV.
- **Two-handed structures:** Additional challenges when handling symmetry and non-dominant hand parameters.

The current extraction method preserves the remaining HamNoSys string as MOV, but this does not always guarantee correct movement boundaries.

## 3. Decision

Following the latest discussion with Sarah, the current focus is on **SS pseudosign generation only**.

CC generation is temporarily postponed because of its additional technical complexity. I will continue on this in the future if possible.

All existing CC classification results, parser tests, extraction results, and structural analyses will be kept for possible future work.

## 4. Possible Future Steps

If time allows, I can continue working on CC generation in the following sections:

1. Improving parameter extraction for complex HamNoSys structures.
2. Checking movement boundaries, especially for replacement and two-handed signs.
3. Preserving complete movement structures during parameter recombination.
4. Applying the existing A/B/C/D source-combination rules to CC signs.
5. Generating poses for CC pseudosigns and evaluating the results.
