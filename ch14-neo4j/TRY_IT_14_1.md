# Try It Yourself 14.1 — operate Neo4j like a production engineer

Run from this folder with the lab stack up (`docker compose up -d` at the
repository root). Each part is independent.

| Part | Command | What you learn |
|---|---|---|
| 1. Size memory | `./memory.sh 8g` | Neo4j's own heap and page-cache recommendation for an 8 GB machine, from your store's real size (§14.3) |
| 2. Tune a query | `python profile_lab.py` | A function on an indexed property forces a label scan (400,001 db hits on 200,000 nodes); a stored, indexed normalized value fixes it (3 db hits) (§14.5) |
| 3. Bulk import | `./admin_import.sh` | `neo4j-admin database import` builds a 1M-node, 5M-relationship database from CSV offline, into a throwaway volume (§14.7) |
| 4. Back up and restore | `./backup_restore.sh` | An offline dump of the lab database and a *verified* restore into a throwaway copy (§14.12) |

Then, in Neo4j Browser (http://localhost:7474):

```cypher
SHOW INDEXES;                 // what exists, and is it ONLINE?
SHOW CONSTRAINTS;
SHOW TRANSACTIONS;            // what is running right now
:sysinfo                      // store sizes, page cache, transactions
```

Part 3 uses smaller data if you set `PEOPLE` and `FOLLOWS`, for example
`PEOPLE=100000 FOLLOWS=500000 ./admin_import.sh`.
