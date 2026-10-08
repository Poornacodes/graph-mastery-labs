"""Listings 5.3 and 5.4 with rdflib — no server needed.

  python sparql_lab.py              # Listing 5.3 against knows.ttl
  python sparql_lab.py --wikidata   # also Listing 5.4 (needs internet)
"""
import sys
from pathlib import Path

from rdflib import Graph

HERE = Path(__file__).resolve().parent


def queries(path):
    """Split a .rq file holding several SELECTs (sharing its PREFIX lines)."""
    text = path.read_text()
    prefixes = "\n".join(l for l in text.splitlines() if l.startswith("PREFIX"))
    body = "\n".join(l for l in text.splitlines()
                     if not l.startswith("PREFIX") and not l.startswith("#"))
    return [prefixes + "\nSELECT" + part for part in body.split("SELECT")[1:]]


def run_5_3():
    g = Graph().parse(HERE / "knows.ttl")
    labels = ["direct", "friend-of-friend", "reachable"]
    answers = {}
    for label, q in zip(labels, queries(HERE / "listing_5_3.rq")):
        answers[label] = sorted(str(r.name) for r in g.query(q))
        print(f"SPARQL {label:<17}", answers[label])
    return answers


if __name__ == "__main__":
    run_5_3()
    if "--wikidata" in sys.argv:
        g = Graph()
        for row in g.query((HERE / "listing_5_4_federation.rq").read_text()):
            print("Wikidata cat:", row.item, row.label)
