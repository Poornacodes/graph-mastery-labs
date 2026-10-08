"""Try It Yourself 11.1 — text in, a validated knowledge graph out.

  extract (Listing 11.1's prompt; your LLM, or the cached output offline)
  -> keep only allowed types (the closed schema)
  -> resolve obvious duplicates ("J. Tan" = "Joanna Tan")
  -> MERGE into Neo4j (Listing 11.2: idempotent)
  -> query it, multi-hop
  -> validate it with SHACL

  LLM_PROVIDER=offline python try_it_11_1.py     # default, no model
  LLM_PROVIDER=ollama  python try_it_11_1.py     # or anthropic / bedrock
"""
import json
import re
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from graphlab import config, neo
from graphlab.llm import call_llm, parse_json
from graphlab.resolve import clusters

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, RDF

ENTITY_TYPES = {"Person", "Company", "Product"}
RELATIONS = {"WORKS_AT", "FOUNDED", "ACQUIRED", "COMPETES_WITH"}
PROMPT = (HERE / "prompt.txt").read_text()


def build_prompt(chunk):
    return PROMPT.replace("{chunk}", chunk)


def extract(name, chunk, cache):
    """Listing 11.2's extract(), with the cached output as the offline path."""
    if config.LLM_PROVIDER == "offline":
        return cache.get(name, [])
    triples = parse_json(call_llm(build_prompt(chunk)))
    if triples is None:
        print(f"  ! {name}: malformed output skipped (log it for review)")
        return []
    return triples


def in_schema(t):
    return (isinstance(t, dict) and t.get("relation") in RELATIONS
            and t.get("head_type") in ENTITY_TYPES
            and t.get("tail_type") in ENTITY_TYPES
            and t.get("head") and t.get("tail"))


# --- entity resolution (Section 11.4): graphlab/resolve.py ---------------
def resolve(triples):
    names = {}
    for t in triples:
        names.setdefault(t["head"], t["head_type"])
        names.setdefault(t["tail"], t["tail_type"])
    canonical = clusters(names)
    merged = {a: c for a, c in canonical.items() if a != c}
    out = [{**t, "head": canonical[t["head"]], "tail": canonical[t["tail"]]}
           for t in triples]
    return out, merged


# --- Listing 11.2's loader -----------------------------------------------
def load_triples(tx, triples):
    tx.run("""
        UNWIND $triples AS t
        MERGE (h:Entity {name: t.head})   ON CREATE SET h.type = t.head_type
        MERGE (a:Entity {name: t.tail})   ON CREATE SET a.type = t.tail_type
        MERGE (h)-[r:REL {type: t.relation}]->(a)
    """, triples=triples)


def shacl_check():
    KG = Namespace("http://graphmastery.example/kg/")
    g = Graph()
    iri = lambda name: KG[re.sub(r"\W+", "_", name)]
    for row in neo.run("MATCH (e:Entity) RETURN e.name AS n, e.type AS t"):
        g.add((iri(row["n"]), RDF.type, KG.Entity))
        g.add((iri(row["n"]), RDF.type, KG[row["t"]]))
        g.add((iri(row["n"]), KG.name, Literal(row["n"])))
        g.add((iri(row["n"]), KG.type, Literal(row["t"])))
    for row in neo.run("MATCH (a:Entity)-[r:REL]->(b:Entity) "
                       "RETURN a.name AS a, r.type AS r, b.name AS b"):
        g.add((iri(row["a"]), KG[row["r"]], iri(row["b"])))
    conforms, _, report = validate(g, shacl_graph=str(HERE / "shapes.ttl"))
    return conforms, report


def main():
    cache = json.loads((HERE / "cached_triples.json").read_text())
    print(f"Extracting with LLM_PROVIDER={config.LLM_PROVIDER}")
    raw = []
    for doc in sorted((HERE / "corpus").glob("*.txt")):
        got = extract(doc.name, doc.read_text(), cache)
        print(f"  {doc.name}: {len(got)} triples")
        raw += got
    kept = [t for t in raw if in_schema(t)]
    for t in raw:
        if not in_schema(t):
            print(f"  - rejected (outside the schema): {t.get('head')} "
                  f"{t.get('relation')} {t.get('tail')}")

    triples, merged = resolve(kept)
    for alias, canon in merged.items():
        print(f"  = resolved {alias!r} -> {canon!r}")

    neo.reset(["Entity"])
    with config.driver() as drv, drv.session() as s:
        s.execute_write(lambda tx: tx.run(
            "CREATE CONSTRAINT entity_name IF NOT EXISTS "
            "FOR (e:Entity) REQUIRE e.name IS UNIQUE"))
        s.execute_write(load_triples, triples)
        s.execute_write(load_triples, triples)        # again: idempotent
    count = neo.run("MATCH (:Entity)-[r:REL]->() RETURN count(r) AS n")[0]["n"]
    print(f"Loaded {count} relationships (the second load added none).")

    print("\nMulti-hop: who works at a company that acquired another company,"
          "\nand who founded the company it bought?")
    for r in neo.run("""
        MATCH (p:Entity)-[:REL {type:'WORKS_AT'}]->(c:Entity)
              -[:REL {type:'ACQUIRED'}]->(t:Entity)<-[:REL {type:'FOUNDED'}]-(f)
        RETURN c.name AS company, t.name AS acquired, f.name AS founder,
               collect(p.name) AS employees"""):
        print("  ", r)

    conforms, report = shacl_check()
    print("\nSHACL conforms:", conforms)
    if not conforms:
        print(report)
    print("\nNext: examples/athena runs the whole loop at larger scale — "
          "extraction,\nresolution, and GraphRAG answers with citations over "
          "the extracted graph.")


if __name__ == "__main__":
    main()
