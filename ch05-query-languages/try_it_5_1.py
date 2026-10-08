"""Try It Yourself 5.1 — one graph, the same two questions, three languages.

Cypher runs on Neo4j, SPARQL runs locally with rdflib, and Gremlin runs on
JanusGraph if you started it (docker compose --profile gremlin up -d).
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from graphlab import neo
import sparql_lab

results = {}

neo.run("MATCH (p:Person) WHERE p.name IN ['Alice','Bob','Carol','Dave'] "
        "DETACH DELETE p")
neo.run_file(HERE / "knows.cypher")
direct, fof = neo.run_file(HERE / "listing_5_1.cypher")
results["Cypher"] = {"direct": sorted(r["friend.name"] for r in direct),
                     "friend-of-friend": sorted(r["fof.name"] for r in fof)}

results["SPARQL"] = {k: v for k, v in sparql_lab.run_5_3().items()
                     if k != "reachable"}

try:
    import gremlin_lab
    results["Gremlin"] = gremlin_lab.run_5_2()
except Exception as exc:  # server not running
    print(f"(Gremlin skipped: {type(exc).__name__}. Start it with "
          "`docker compose --profile gremlin up -d`.)")

print()
for lang, ans in results.items():
    print(f"{lang:<8} direct={ans['direct']}  friend-of-friend={ans['friend-of-friend']}")
answers = {str(a) for a in results.values()}
print("\nAll languages agree:", len(answers) == 1)
print("\nGQL form (listing_5_5.gql) — note how closely it mirrors Cypher; this\n"
      "exact text also runs as Cypher in Neo4j:")
print((HERE / "listing_5_5.gql").read_text())
assert len(answers) == 1
