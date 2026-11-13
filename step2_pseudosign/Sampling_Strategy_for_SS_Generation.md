### Sampling Strategy for SS Generation

Since the total number of possible SS source combinations is very large (around 36.9 billion), generating all combinations would not be practical. 

Therefore, I decided to use a stratified sampling approach.

The candidates are divided into 16 groups based on four structural modes (single, sym_e0e9, sym_e0e8, and asym_two) and four recombination categories (A–D).

According to Edwards (2024) and Shalabh (Sampling Theory, Chapter 4), stratified sampling allows samples to be selected separately from different groups. 

Equal allocation can also help ensure that smaller groups are represented, rather than letting larger groups dominate the sample.

I initially considered selecting 200 candidates from each group. 

However, since the source pools differ considerably in size and parameter diversity, I tested three sample sizes (100, 200, and 300) for each group. 

I compared the number of unique HamNoSys strings and unique HF, HP, LOC, and MOV parameter values.

Based on these results:

- **Single and sym_e0e9:** Parameter diversity was still increasing at 300 candidates, so I selected 300 per category.

- **Asym_two:** Most observed parameter values were already covered by around 100–200 candidates, so I selected 200 per category.

- **Sym_e0e8:** Parameter diversity became stable quite early, but new HamNoSys combinations were still appearing. 
I selected 300 for categories B, C, and D. For category A, there are only 48 theoretically possible source combinations, so all 48 will be checked.

This gives a target of approximately 4,148 provenance records across the 16 groups, before accounting for unsuccessful checks and duplicate HamNoSys strings.

The selected numbers are based on the preliminary diversity results and the practical need to keep the candidate pool manageable for further processing and evaluation. 

They are not intended to provide a statistically representative sample of all possible pseudosigns.

**References**

- Edwards, K. (2024). Stratified Sampling: A Comprehensive Guide. SurveyLab. https://www.surveylab.com/blog/stratified-sampling/
- Shalabh. Sampling Theory, Chapter 4: Stratified Sampling. IIT Kanpur. https://home.iitk.ac.in/~shalab/sampling/chapter4-sampling-stratified-sampling.pdf