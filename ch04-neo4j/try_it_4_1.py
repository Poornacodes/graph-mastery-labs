"""Try It Yourself 4.1 — load the movie graph, answer the three questions,
then PROFILE a query and confirm it starts with an index seek."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from graphlab import config, neo

neo.reset(["Viewer", "Movie"])
neo.run_file(HERE / "try_it_4_1_data.cypher")

names = ["Q1 Ana's five-star movies", "Q2 average rating per movie",
         "Q3 recommendations for Ana"]
for name, rows in zip(names, neo.run_file(HERE / "try_it_4_1_solution.cypher")):
    print(f"--- {name}")
    for row in rows:
        print("   ", row)

# PROFILE: the plan should begin with an index seek on Viewer.name (the
# uniqueness constraint created that index), not a NodeByLabelScan.
with config.driver() as drv:
    _, summary, _ = drv.execute_query(
        "PROFILE MATCH (v:Viewer {name:'Ana'})-[:RATED]->(m) RETURN m.title")

def operators(plan):
    yield plan["operatorType"]
    for child in plan.get("children", []):
        yield from operators(child)

ops = list(operators(summary.profile))
seek = [o for o in ops if "IndexSeek" in o]
print("--- PROFILE operators:", ", ".join(o.split("@")[0] for o in ops))
print("Anchored on an index seek:", bool(seek))
assert seek, "Expected an index seek; is the viewer_name constraint present?"
