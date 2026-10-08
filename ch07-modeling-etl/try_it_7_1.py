"""Try It Yourself 7.1 — generate, load, count, load again, count again.

The counts must be identical: MERGE (u)-[r:RATED]->(p) matches the existing
relationship on the second run instead of creating a duplicate, because the
whole pattern (this user, this product, a RATED edge between them) already
exists. CREATE would double every count.
"""
import subprocess
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from graphlab import neo

COUNT = """MATCH (u:User) WITH count(u) AS users
           MATCH (p:Product) WITH users, count(p) AS products
           MATCH (:User)-[r:RATED]->(:Product)
           RETURN users, products, count(r) AS ratings"""

subprocess.run([sys.executable, str(HERE / "generate_ratings.py")], check=True)
neo.reset(["User", "Product"])
counts = []
for attempt in (1, 2):
    subprocess.run([sys.executable, str(HERE / "listing_7_1_loader.py")],
                   check=True, cwd=HERE)
    counts.append(neo.run(COUNT)[0])
    print(f"After load {attempt}: {counts[-1]}")
print("Idempotent:", counts[0] == counts[1])
assert counts[0] == counts[1]
