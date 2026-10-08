"""Section E.8 / Listing E.7 — The Athena API.

  uvicorn api:app --reload        (from examples/athena/)
  open http://localhost:8000/     ask a question, see the cited subgraph
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from rag import answer, run_cypher

app = FastAPI(title="Athena")

@app.get("/ask")
def ask(q: str):
    text, citations = answer(q)
    return {"answer": text,
            "citations": [c["seed_entities"] for c in citations]}

@app.get("/graph/entity/{name}")
def entity_graph(name: str, limit: int = 40):
    # returns {nodes, edges} for visualization, capped at `limit` (Ch 8)
    rows = run_cypher("""
        MATCH (e:Entity {name: $name})-[r:REL]-(n:Entity)
        RETURN e.name AS a, e.type AS at, r.type AS rel, n.name AS b,
               n.type AS bt, startNode(r) = e AS outgoing
        LIMIT $limit""", name=name, limit=limit)
    nodes, edges = {}, []
    for r in rows:
        nodes[r["a"]] = {"id": r["a"], "label": r["a"], "group": r["at"]}
        nodes[r["b"]] = {"id": r["b"], "label": r["b"], "group": r["bt"]}
        src, dst = (r["a"], r["b"]) if r["outgoing"] else (r["b"], r["a"])
        edges.append({"from": src, "to": dst, "label": r["rel"]})
    return {"nodes": list(nodes.values()), "edges": edges}

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).with_name("static") / "index.html")
