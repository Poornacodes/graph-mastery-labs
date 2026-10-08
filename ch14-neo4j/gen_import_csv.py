"""Write CSV files in neo4j-admin import format: N people, M FOLLOWS edges.

  python gen_import_csv.py --people 1000000 --follows 5000000
"""
import argparse
import csv
import random
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--people", type=int, default=1_000_000)
ap.add_argument("--follows", type=int, default=5_000_000)
ap.add_argument("--out", default=str(Path(__file__).with_name("import-demo")))
a = ap.parse_args()
out = Path(a.out); out.mkdir(exist_ok=True)
rnd = random.Random(14)
with open(out / "persons.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["personId:ID", "name", "age:int", ":LABEL"])
    for i in range(a.people):
        w.writerow([i, f"person{i}", 18 + i % 60, "Person"])
with open(out / "follows.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow([":START_ID", ":END_ID", "since:int", ":TYPE"])
    for _ in range(a.follows):
        w.writerow([rnd.randrange(a.people), rnd.randrange(a.people),
                    2010 + rnd.randrange(15), "FOLLOWS"])
print(f"wrote {a.people:,} people and {a.follows:,} follows to {out}")
