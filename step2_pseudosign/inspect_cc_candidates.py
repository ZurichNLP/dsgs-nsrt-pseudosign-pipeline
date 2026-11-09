
import csv
from pathlib import Path

# Read the classification results from Step 1.
root = Path(__file__).resolve().parent.parent
csv_path = root / "step1_classification/output/analysis_ready_pool.csv"

with open(csv_path, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Select CC signs with one PM and one IM.
candidates = [
    row for row in rows
    if row["handshape_dsgs"] == "complex"
    and row["movement_class"] == "complex"
    and int(row["pm_count"]) == 1
    and int(row["im_count"]) == 1
]

print(f"Found {len(candidates)} CC candidates.\n")

for row in candidates[:10]:
    print("Gloss:", row["gloss_id"])
    print("Handshape:", row["handshape_dsgs"])
    print("Movement:", row["movement_class"])
    print("HamNoSys:", " ".join(
        f"U+{ord(c):04X}" for c in row["hamnosys"]
    ))
    print("-" * 60)
