"""An honest comparison (Chapter 4, section 4.1.1): the same friendship graph
in PostgreSQL and in Neo4j, asked the same question -- "how many people are
within k hops of this person?" -- for k = 1 to 5.

Both databases run in Docker on the same machine with their default settings.
Each side uses one long-lived connection (a psycopg connection; one Neo4j
session), and the script reports two timings: end to end as the Python client
sees it, and server-side execution time as each database reports it
(PostgreSQL's EXPLAIN ANALYZE; Neo4j's result summary).
The SQL is written the way an experienced SQL developer would write it
(deduplicate each hop before taking the next), not as a naive join chain, so
the comparison is fair to the relational side.

Run:  python ch04-neo4j/pg_vs_neo4j.py           (needs Docker and the lab Neo4j)
It starts a throwaway PostgreSQL container, loads both databases, checks that
both return identical answers, times them, prints a table, and cleans up.
"""
from __future__ import annotations

import io
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import psycopg  # noqa: E402

from graphlab import config  # noqa: E402

N_PEOPLE = 100_000        # people
FRIENDS_EACH = 5          # random friendships started by each person (avg degree ~10)
HOPS = [1, 2, 3, 4, 5]
STARTS = 30               # random start people timed per hop count
SEED = 7
PG_PORT, PG_PASS, PG_NAME = 15432, "bench", "gm-pg-bench"
LABEL = "Bench4"


def make_edges():
    rnd = random.Random(SEED)
    edges = set()
    for a in range(N_PEOPLE):
        for _ in range(FRIENDS_EACH):
            b = rnd.randrange(N_PEOPLE)
            if a != b:
                edges.add((min(a, b), max(a, b)))
    return sorted(edges)


# ------------------------------------------------------------------ PostgreSQL
def pg_start():
    subprocess.run(["docker", "rm", "-f", PG_NAME], capture_output=True)
    subprocess.run(["docker", "run", "-d", "--rm", "--name", PG_NAME,
                    "-e", f"POSTGRES_PASSWORD={PG_PASS}", "-p", f"{PG_PORT}:5432",
                    "postgres:16"], check=True, capture_output=True)
    for _ in range(60):
        try:
            return psycopg.connect(f"host=localhost port={PG_PORT} user=postgres "
                                   f"password={PG_PASS}", autocommit=True)
        except psycopg.OperationalError:
            time.sleep(1)
    raise SystemExit("PostgreSQL did not start")


def pg_load(conn, edges):
    conn.execute("CREATE TABLE people (id int PRIMARY KEY)")
    conn.execute("CREATE TABLE friends (a int NOT NULL, b int NOT NULL)")
    with conn.cursor().copy("COPY people (id) FROM STDIN") as cp:
        for i in range(N_PEOPLE):
            cp.write_row((i,))
    with conn.cursor().copy("COPY friends (a, b) FROM STDIN") as cp:
        for a, b in edges:              # store both directions, as SQL designs do
            cp.write_row((a, b))
            cp.write_row((b, a))
    conn.execute("CREATE INDEX friends_a_b ON friends (a, b)")   # covering index
    conn.execute("VACUUM ANALYZE friends")


def pg_sql(k):
    """Distinct people within k hops: deduplicate each hop's frontier, then union."""
    hops = ["s1 AS (SELECT DISTINCT b AS id FROM friends WHERE a = %(s)s)"]
    for i in range(2, k + 1):
        hops.append(f"s{i} AS (SELECT DISTINCT f.b AS id FROM s{i-1} "
                    f"JOIN friends f ON f.a = s{i-1}.id)")
    union = " UNION ".join(f"SELECT id FROM s{i}" for i in range(1, k + 1))
    return (f"WITH {', '.join(hops)} "
            f"SELECT count(*) FROM ({union}) u WHERE id <> %(s)s")


# ---------------------------------------------------------------------- Neo4j
def neo_load(drv, edges):
    neo_cleanup(drv)
    drv.execute_query(f"CREATE CONSTRAINT bench4_id IF NOT EXISTS "
                      f"FOR (p:{LABEL}) REQUIRE p.id IS UNIQUE")
    for lo in range(0, N_PEOPLE, 50_000):
        drv.execute_query(f"UNWIND range($lo, $hi) AS i CREATE (:{LABEL} {{id: i}})",
                          lo=lo, hi=min(lo + 50_000, N_PEOPLE) - 1)
    for lo in range(0, len(edges), 50_000):
        batch = [{"a": a, "b": b} for a, b in edges[lo:lo + 50_000]]
        drv.execute_query(f"UNWIND $rows AS r MATCH (a:{LABEL} {{id: r.a}}), "
                          f"(b:{LABEL} {{id: r.b}}) CREATE (a)-[:FRIEND]->(b)",
                          rows=batch)


def neo_cypher(k):
    # Each friendship is stored once and queried in both directions.
    return (f"MATCH (p:{LABEL} {{id: $s}})-[:FRIEND*1..{k}]-(x) "
            f"WHERE x <> p RETURN count(DISTINCT x) AS n")


def neo_cleanup(drv):
    while True:
        recs, _, _ = drv.execute_query(f"MATCH (n:{LABEL}) WITH n LIMIT 20000 "
                                       f"DETACH DELETE n RETURN count(*) AS c")
        if recs[0]["c"] == 0:
            break
    drv.execute_query("DROP CONSTRAINT bench4_id IF EXISTS")


# --------------------------------------------------------------------- timing
def timed(fn):
    t = time.perf_counter()
    result = fn()
    return result, (time.perf_counter() - t) * 1000


def main():
    edges = make_edges()
    print(f"{N_PEOPLE:,} people, {len(edges):,} friendships "
          f"(average {2 * len(edges) / N_PEOPLE:.1f} friends each)")
    pg = pg_start()
    drv = config.driver()
    try:
        _, t = timed(lambda: pg_load(pg, edges))
        print(f"PostgreSQL loaded in {t / 1000:.1f} s")
        _, t = timed(lambda: neo_load(drv, edges))
        print(f"Neo4j loaded in {t / 1000:.1f} s")
        rnd = random.Random(SEED + 1)
        rows = []
        sess = drv.session()
        for k in HOPS:
            starts = [rnd.randrange(N_PEOPLE) for _ in range(STARTS if k < 5 else 10)]
            sql, cy = pg_sql(k), neo_cypher(k)
            # warm both caches with the first start, and check the answers agree
            for s in starts[:3]:
                a = pg.execute(sql, {"s": s}).fetchone()[0]
                b = sess.run(cy, s=s).single()["n"]
                if a != b:
                    raise SystemExit(f"answers differ at k={k}, start {s}: {a} vs {b}")
            pg_ms, neo_ms, pg_srv, neo_srv, reach = [], [], [], [], []
            for s in starts:
                n, t = timed(lambda: pg.execute(sql, {"s": s}).fetchone()[0])
                pg_ms.append(t); reach.append(n)
                plan = pg.execute("EXPLAIN (ANALYZE, TIMING OFF, FORMAT JSON) " + sql,
                                  {"s": s}).fetchone()[0]
                pg_srv.append(plan[0]["Execution Time"])
                res, t = timed(lambda: sess.run(cy, s=s).consume())
                neo_ms.append(t)
                neo_srv.append(res.result_available_after + res.result_consumed_after)
            med = statistics.median
            rows.append((k, med(reach), med(pg_ms), med(neo_ms), med(pg_srv), med(neo_srv)))
            print(f"  k={k}: reach {med(reach):>9,.0f}   PostgreSQL {med(pg_ms):>7.1f} ms "
                  f"(server {med(pg_srv):>6.1f})   Neo4j {med(neo_ms):>7.1f} ms "
                  f"(server {med(neo_srv):>6.1f})", flush=True)
        sess.close()
        print("\nMedian milliseconds over the timed starts (end to end / server-side)")
        print("hops | people reached | PostgreSQL       | Neo4j")
        for k, r, a, b, c, d in rows:
            print(f"{k:>4} | {r:>14,.0f} | {a:>6.1f} / {c:>6.1f} | {b:>6.1f} / {d:>6.1f}")
    finally:
        neo_cleanup(drv)
        drv.close()
        pg.close()
        subprocess.run(["docker", "rm", "-f", PG_NAME], capture_output=True)


if __name__ == "__main__":
    main()
