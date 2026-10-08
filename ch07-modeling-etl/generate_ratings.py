"""Try It Yourself 7.1 — generate a synthetic users-rate-products dataset.

Writes data/products.csv and data/ratings.csv. Users have a taste for one or
two product categories, so co-rating patterns are realistic enough for the
Chapter 8 recommender to produce sensible results.

  python generate_ratings.py --users 200 --products 60 --seed 7
"""
import argparse
import csv
import random
from pathlib import Path

CATEGORIES = {
    "Books":       ["Graph Theory Primer", "Network Science", "Data Modeling",
                    "SPARQL by Example", "Cypher Cookbook", "Knowledge Graphs",
                    "Linked Data", "Algorithms Illustrated"],
    "Electronics": ["USB-C Hub", "Mechanical Keyboard", "Noise-Cancelling Headset",
                    "4K Monitor", "Webcam", "Laptop Stand", "Portable SSD",
                    "Wireless Mouse"],
    "Outdoors":    ["Trail Shoes", "Rain Jacket", "Daypack", "Water Filter",
                    "Headlamp", "Camp Stove", "Trekking Poles", "Sleeping Pad"],
    "Kitchen":     ["Chef's Knife", "Cast-Iron Pan", "Pour-Over Kettle",
                    "Burr Grinder", "Cutting Board", "Dutch Oven",
                    "Spice Rack", "Stand Mixer"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", type=int, default=200)
    ap.add_argument("--products", type=int, default=32)
    ap.add_argument("--per-user", type=int, default=8)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=str(Path(__file__).with_name("data")))
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    products = []
    names = [(c, n) for c, ns in CATEGORIES.items() for n in ns]
    for pid in range(1, a.products + 1):
        cat, name = names[(pid - 1) % len(names)]
        if pid > len(names):
            name = f"{name} v{(pid - 1) // len(names) + 1}"
        products.append({"product_id": pid, "name": name, "category": cat})
    with open(out / "products.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["product_id", "name", "category"])
        w.writeheader()
        w.writerows(products)

    by_cat = {}
    for p in products:
        by_cat.setdefault(p["category"], []).append(p["product_id"])
    rows = []
    for uid in range(1, a.users + 1):
        tastes = rnd.sample(sorted(by_cat), k=rnd.choice([1, 2]))
        pool = [pid for c in tastes for pid in by_cat[c]]
        others = [p["product_id"] for p in products if p["product_id"] not in pool]
        picks = set(rnd.sample(pool, k=min(a.per_user - 1, len(pool))))
        picks.add(rnd.choice(others))             # one off-taste purchase
        for pid in sorted(picks):
            stars = rnd.choice([4, 5, 5]) if pid in pool else rnd.choice([1, 2, 3])
            rows.append({"user_id": uid, "product_id": pid, "stars": stars})
    with open(out / "ratings.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["user_id", "product_id", "stars"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(products)} products and {len(rows)} ratings to {out}")


if __name__ == "__main__":
    main()
