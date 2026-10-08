"""Listings 8.1 and 8.2 — a recommendation API over Neo4j, plus the
explainable variant from Try It Yourself 8.1.

  python ../ch07-modeling-etl/generate_ratings.py
  python ../ch07-modeling-etl/listing_7_1_loader.py   # from ch07's folder
  uvicorn app:app --reload
  open http://localhost:8000/docs  and  http://localhost:8000/

The driver reads NEO4J_URI and NEO4J_PASSWORD from the environment (defaults:
bolt://localhost:7687, graphmastery), so the same file runs inside the
Chapter 12 Docker Compose stack, where the database is bolt://neo4j:7687.
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"),
          os.getenv("NEO4J_PASSWORD", "graphmastery")))

@asynccontextmanager
async def lifespan(app):
    yield                       # serve requests
    driver.close()              # then release the pool on shutdown

app = FastAPI(title="Graph Recommender", lifespan=lifespan)

# Listing 8.1 — A recommendation API over Neo4j
@app.get("/users/{uid}/recommendations")
def recommendations(uid: int, limit: int = 5):
    q = """
    MATCH (me:User {id:$uid})-[:RATED]->(p)<-[:RATED]-(other)
          -[:RATED]->(rec:Product)
    WHERE NOT (me)-[:RATED]->(rec) AND rec <> p
    RETURN rec.id AS id, rec.name AS name, count(DISTINCT other) AS score
    ORDER BY score DESC LIMIT $limit
    """
    with driver.session() as s:
        rows = s.run(q, uid=uid, limit=limit).data()
    if not rows:
        raise HTTPException(404, "No recommendations for this user")
    return {"user_id": uid, "recommendations": rows}

# Try It Yourself 8.1 — the explainable variant: each suggestion also returns
# *why*: the products you share with the people who liked it
@app.get("/users/{uid}/recommendations/explained")
def explained(uid: int, limit: int = 5):
    q = """
    MATCH (me:User {id:$uid})-[mine:RATED]->(p)<-[theirs:RATED]-(other)
          -[liked:RATED]->(rec:Product)
    WHERE mine.stars >= 4 AND theirs.stars >= 4 AND liked.stars >= 4
      AND NOT (me)-[:RATED]->(rec) AND rec <> p
    WITH rec, count(DISTINCT other) AS score,
         collect(DISTINCT p.name)[..3] AS because_you_liked
    RETURN rec.id AS id, rec.name AS name, score, because_you_liked
    ORDER BY score DESC LIMIT $limit
    """
    with driver.session() as s:
        rows = s.run(q, uid=uid, limit=limit).data()
    if not rows:
        raise HTTPException(404, "No recommendations for this user")
    return {"user_id": uid, "recommendations": rows}

# Listing 8.2 — A graph endpoint for visualization
@app.get("/graph/users/{uid}")
def user_graph(uid: int, limit: int = 40):
    q = """
    MATCH (u:User {id:$uid})-[r:RATED]->(p:Product)
    RETURN u.id AS uid, p.id AS pid, p.name AS pname, r.stars AS stars
    LIMIT $limit
    """
    with driver.session() as s:
        rows = s.run(q, uid=uid, limit=limit).data()
    me = f"u{uid}"
    nodes = {me: {"id": me, "label": f"User {uid}", "group": "user"}}
    edges = []
    for row in rows:
        pnode = f"p{row['pid']}"
        nodes[pnode] = {"id": pnode, "label": row["pname"],
                        "group": "product"}
        edges.append({"from": me, "to": pnode,
                      "label": f"{row['stars']}*"})
    return {"nodes": list(nodes.values()), "edges": edges}

# Listing 8.3's page, served at /
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).with_name("static") / "index.html")
