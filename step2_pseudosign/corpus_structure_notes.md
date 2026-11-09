# Corpus Structure Analysis

**Script:** `analyze_corpus_structures.py`  
**Input:** `analysis_ready_pool.csv` (2,319 signs)

## Results

- Classification: SS = 1103; SC = 795; CS = 243; CC = 178.
- Target source pool: 1,281 SS and CC signs.
- SS: parallel 19.4%, replacement 26.7%, sequence 14.1%, fusion 1.5%, repetition 49.0%, nested parallel 0.4%.
- CC: parallel 100%, replacement 96.1%, sequence 14.6%, fusion 2.2%, repetition 19.1%, nested parallel 12.4%.
- Two SS signs were flagged for unmatched structural markers: `ELEKTROMONTEUR_1A` and `HAND_1A`.

## Key Findings

1. SS signs may contain complex HamNoSys structures, although they have simple handshape and movement classifications.
2. Replacement markers are present in 171 of 178 CC signs (96.1%). Therefore, replacement handling is essential for CC generation.
3. Parallel brackets need to be preserved, but not all parallel structures necessarily indicate simultaneous PM and IM.
4. Nested structures and two-handed signs require additional checks.
