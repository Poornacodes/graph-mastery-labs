"""Run every Chapter 4 listing against your local Neo4j and print results."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from graphlab import neo

neo.run("DROP CONSTRAINT person_name IF EXISTS")
neo.reset(["Person", "Company"])
neo.run_file(HERE / "seed_social.cypher")

titles = ["4.1 people over 25 and their companies", "4.2 MERGE Alice",
          "update Alice's age", "4.3 companies with more than 10 people",
          "4.4 friends within three hops of Alice",
          "4.4 shortest path Alice -> Zoe", "4.5 LOAD CSV people",
          "4.7 uniqueness constraint", "4.7 age index",
          "4.8 PROFILE"]
for title, rows in zip(titles, neo.run_file(HERE / "listings_4_1_to_4_8.cypher")):
    print(f"--- Listing {title}")
    for row in rows[:12]:
        if "p" in row and isinstance(row["p"], list):   # a path
            row = {"path": [x["name"] for x in row["p"] if isinstance(x, dict)],
                   "length": row["length(p)"]}
        print("   ", row)

print("--- Listing 4.9 (Graph Data Science)")
neo.run("CALL gds.graph.exists('social') YIELD exists "
        "WITH exists WHERE exists CALL gds.graph.drop('social') YIELD graphName "
        "RETURN graphName")
for rows in neo.run_file(HERE / "listing_4_9_gds.cypher")[2:3]:
    for row in rows:
        print("   ", row)
