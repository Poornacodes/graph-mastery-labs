// Chapter 4 listings, in book order. Run seed_social.cypher first (or use
// run_listings.py, which does both). Paste into Neo4j Browser
// (http://localhost:7474) one statement at a time to see each result.

// Listing 4.1 — A basic read
MATCH (p:Person)-[:WORKS_AT]->(c:Company)
WHERE p.age > 25
RETURN p.name, c.name;

// Listing 4.2 — CREATE versus the idempotent MERGE
// (CREATE would add a second Alice, so it is shown commented out here)
// CREATE (p:Person {name:'Alice', age:30});  // always inserts (can duplicate)
MERGE (p:Person {name:'Alice'})            // idempotent: safe to re-run
  ON CREATE SET p.created = timestamp()
  ON MATCH  SET p.lastSeen = timestamp();

// Updating (the DETACH DELETE form is shown commented out so the rest of the
// listings still have Alice to work with)
MATCH (p:Person {name:'Alice'}) SET p.age = 31;
// MATCH (p:Person {name:'Alice'}) DETACH DELETE p;

// Listing 4.3 — Aggregation through the WITH pipe
MATCH (p:Person)-[:WORKS_AT]->(c:Company)
WITH c, count(p) AS headcount
WHERE headcount > 10
RETURN c.name, headcount ORDER BY headcount DESC;

// Listing 4.4 — Variable-length and shortest paths
// Friends up to three hops away
MATCH (me:Person {name:'Alice'})-[:FRIEND*1..3]-(fof)
WHERE fof <> me
RETURN DISTINCT fof.name;

// Shortest path between two people
MATCH p = shortestPath(
  (a:Person {name:'Alice'})-[:FRIEND*]-(b:Person {name:'Zoe'}))
RETURN p, length(p);

// Listing 4.5 — Idempotent CSV import (people.csv is in the import/ folder,
// which docker-compose.yml mounts as Neo4j's import directory)
LOAD CSV WITH HEADERS FROM 'file:///people.csv' AS row
MERGE (p:Person {id: row.id})
  SET p.name = row.name, p.age = toInteger(row.age);

// Listing 4.7 — A uniqueness constraint (which also creates an index)
CREATE CONSTRAINT person_name IF NOT EXISTS
FOR (p:Person) REQUIRE p.name IS UNIQUE;

CREATE INDEX person_age IF NOT EXISTS FOR (p:Person) ON (p.age);

// Listing 4.8 — Profiling a query
PROFILE
MATCH (p:Person {name:'Alice'})-[:FRIEND]-(f)
RETURN f.name;
