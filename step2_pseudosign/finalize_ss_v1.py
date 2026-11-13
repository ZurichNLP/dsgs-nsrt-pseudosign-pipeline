
import csv
from pathlib import Path

out = Path(__file__).resolve().parent / "output"

quotas = {
    "single": 300,
    "sym_e0e9": 300,
    "sym_e0e8": 300,
    "asym_two": 200,
}

final = []

for mode, n in quotas.items():
    with open(
        out / f"diversity_ss_{mode}.csv",
        encoding="utf-8-sig"
    ) as f:
        rows = list(csv.DictReader(f))

    for category in "ABCD":
        selected = [
            row for row in rows
            if row["category"] == category
        ][:n]

        final.extend(selected)

        print(
            mode, category,
            len(selected),
            "unique:",
            len({r["hamnosys"] for r in selected})
        )

with open(
    out / "final_ss_candidates_v1.csv",
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:
    writer = csv.DictWriter(f, fieldnames=final[0].keys())
    writer.writeheader()
    writer.writerows(final)

print("Total:", len(final))
print("Unique:", len({r["hamnosys"] for r in final}))
