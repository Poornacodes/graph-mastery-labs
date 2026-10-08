"""Run every lab and report what passed, what was skipped, and why.

  python scripts/smoke_test.py          # needs `docker compose up -d` first
  python scripts/smoke_test.py --quick  # skip the slower GraphRAG labs

Optional pieces are skipped, not failed, when they are not set up:
JanusGraph (Gremlin), PyTorch Geometric (Listing 10.3), and any LLM.
"""
import filecmp
import importlib.util
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from graphlab import config  # noqa: E402

results = []


def port_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def run(name, cmd, cwd=ROOT, needs=None):
    if needs:
        missing = [why for ok, why in needs if not ok]
        if missing:
            results.append(("SKIP", name, "; ".join(missing)))
            return
    t = time.time()
    p = subprocess.run([sys.executable, *cmd], cwd=cwd, capture_output=True,
                       text=True)
    took = f"{time.time() - t:.0f}s"
    if p.returncode == 0:
        results.append(("PASS", name, took))
    else:
        tail = (p.stderr or p.stdout).strip().splitlines()[-1:] or [""]
        results.append(("FAIL", name, f"{took}: {tail[0][:150]}"))


def main():
    quick = "--quick" in sys.argv
    neo4j = (port_open("localhost", 7687), "Neo4j not reachable on 7687 "
             "(run `docker compose up -d`)")
    fuseki = (port_open("localhost", 3030), "Fuseki not reachable on 3030")
    gremlin = (port_open("localhost", 8182), "JanusGraph not running "
               "(`docker compose --profile gremlin up -d`)")
    pyg = (importlib.util.find_spec("torch_geometric") is not None,
           "PyTorch Geometric not installed (requirements-gnn.txt)")

    run("Ch 2  Try It 2.1", ["ch02-graph-theory/try_it_2_1.py"])
    for f in ["listing_3_1_bfs.py", "listing_3_2_dfs.py",
              "listing_3_3_dijkstra.py", "listings_3_4_to_3_6.py",
              "try_it_3_1.py"]:
        run(f"Ch 3  {f}", [f"ch03-algorithms/{f}"])
    run("Ch 4  Listings 4.1-4.9", ["ch04-neo4j/run_listings.py"], needs=[neo4j])
    run("Ch 4  Listing 4.6 driver", ["ch04-neo4j/listing_4_6_driver.py"], needs=[neo4j])
    run("Ch 4  Try It 4.1", ["ch04-neo4j/try_it_4_1.py"], needs=[neo4j])
    run("Ch 5  Listing 5.3 (SPARQL)", ["sparql_lab.py"],
        cwd=ROOT / "ch05-query-languages")
    run("Ch 5  Listing 5.2 (Gremlin)", ["gremlin_lab.py"],
        cwd=ROOT / "ch05-query-languages", needs=[gremlin])
    run("Ch 5  Try It 5.1", ["try_it_5_1.py"],
        cwd=ROOT / "ch05-query-languages", needs=[neo4j])
    run("Ch 6  Listings 6.1-6.4", ["ch06-knowledge-graphs/run_listings.py"])
    run("Ch 6  Try It 6.1", ["ch06-knowledge-graphs/try_it_6_1.py"])
    run("Ch 7  Try It 7.1", ["ch07-modeling-etl/try_it_7_1.py"], needs=[neo4j])
    run("Ch 8  Listing 8.4 tests", ["-m", "pytest", "-q", "tests"],
        cwd=ROOT / "ch08-fullstack-app", needs=[neo4j])
    if not quick:
        run("Ch 9  build", ["build.py"], cwd=ROOT / "ch09-graphrag", needs=[neo4j])
        run("Ch 9  ask", ["ask.py"], cwd=ROOT / "ch09-graphrag", needs=[neo4j])
    run("Ch 10 Listing 10.1 (GDS node2vec)", ["ch10-graph-ml/run_listing_10_1.py"],
        needs=[neo4j])
    run("Ch 10 Listing 10.2", ["ch10-graph-ml/listing_10_2_link_prediction.py"])
    run("Ch 10 Listing 10.3 (GCN)", ["ch10-graph-ml/listing_10_3_gcn.py"],
        needs=[pyg])
    run("Ch 11 Try It 11.1", ["ch11-llm-kg/try_it_11_1.py"], needs=[neo4j])
    same = filecmp.cmp(ROOT / "ch08-fullstack-app/app.py",
                       ROOT / "ch12-production/api/app.py", shallow=False)
    results.append(("PASS" if same else "FAIL", "Ch 12 api/app.py matches Ch 8",
                    "" if same else "copy ch08-fullstack-app/app.py to ch12-production/api/"))
    run("Ch 13 Try It 13.1 (local)", ["ch13-neptune/try_it_13_1_local.py"],
        needs=[neo4j, fuseki])
    if not quick:
        run("App E Athena pipeline", ["run_all.py"], cwd=ROOT / "examples/athena",
            needs=[neo4j])

    width = max(len(n) for _, n, _ in results)
    for status, name, note in results:
        print(f"{status:<5} {name:<{width}}  {note}")
    fails = sum(s == "FAIL" for s, _, _ in results)
    print(f"\n{sum(s == 'PASS' for s, _, _ in results)} passed, "
          f"{sum(s == 'SKIP' for s, _, _ in results)} skipped, {fails} failed "
          f"(LLM_PROVIDER={config.LLM_PROVIDER})")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
