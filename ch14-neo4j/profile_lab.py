"""Try It Yourself 14.1, part 2 — diagnose and fix a slow query with PROFILE.

A function wrapped around an indexed property (toLower(c.email) = ...) cannot
use the index, so Neo4j scans every node. The fix: store the normalized value
and index it. Prints each plan's operators and total database hits.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from graphlab import config, neo

N = 200_000


def profile(query, **params):
    with config.driver() as drv:
        _, summary, _ = drv.execute_query("PROFILE " + query, params)
    ops = []
    def walk(p):
        ops.append((p["operatorType"].split("@")[0], p.get("dbHits", 0)))
        for c in p.get("children", []):
            walk(c)
    walk(summary.profile)
    return ops, sum(h for _, h in ops)


def show(title, query, **params):
    ops, hits = profile(query, **params)
    print(f"\n{title}\n  {query.strip()}")
    for op, h in reversed(ops):
        print(f"    {op:<28} {h:>9,} db hits")
    print(f"  total: {hits:,} db hits")
    return hits


def main():
    neo.run("MATCH (c:Customer14) DETACH DELETE c")
    neo.run("DROP INDEX cust_email IF EXISTS")
    neo.run("DROP INDEX cust_email_lower IF EXISTS")
    neo.run("""UNWIND range(1, $n) AS i
               CREATE (:Customer14 {email: 'User' + i + '@Example.com'})""", n=N)
    neo.run("CREATE INDEX cust_email IF NOT EXISTS FOR (c:Customer14) ON (c.email)")
    neo.run("CALL db.awaitIndexes(300)")
    print(f"{N:,} customers loaded; index on email")

    slow = show("1. Case-insensitive lookup with a function: the index is ignored",
                "MATCH (c:Customer14) WHERE toLower(c.email) = $e RETURN c.email",
                e="user4242@example.com")

    neo.run("MATCH (c:Customer14) SET c.emailLower = toLower(c.email)")
    neo.run("CREATE INDEX cust_email_lower IF NOT EXISTS "
            "FOR (c:Customer14) ON (c.emailLower)")
    neo.run("CALL db.awaitIndexes(300)")
    fast = show("2. Fix: store the normalized value once, index it, compare directly",
                "MATCH (c:Customer14) WHERE c.emailLower = $e RETURN c.email",
                e="user4242@example.com")
    print(f"\n{slow:,} -> {fast:,} db hits ({slow // max(fast, 1):,}x less work)")
    for _ in range(N // 50_000 + 1):             # clean up in batches
        neo.run("MATCH (c:Customer14) WITH c LIMIT 50000 DETACH DELETE c")
    neo.run("DROP INDEX cust_email IF EXISTS")
    neo.run("DROP INDEX cust_email_lower IF EXISTS")
    if fast * 100 > slow:                       # the fix must be an index seek
        raise SystemExit("expected the indexed query to need far fewer db hits")


if __name__ == "__main__":
    main()
