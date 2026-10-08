"""Section E.3 / Listing E.2 — Constrained extraction and idempotent load.

Also stores each chunk and links (:Chunk)-[:MENTIONS]->(:Entity) for the
entities extracted from it, which Section E.7's retrieval needs.

  python extract.py      # LLM_PROVIDER=offline replays cached_extractions.json
"""
import json

from common import HERE, load_chunks
from graphlab import config, neo
from graphlab.llm import call_llm, parse_json

driver = config.driver()

ALLOWED_RELATIONS = {"WORKS_ON", "LEADS", "MEMBER_OF", "BUILDS",
                     "DEPENDS_ON", "ANNOUNCES"}

PROMPT = """Extract knowledge triples from the text as JSON.
Use ONLY these types.
Entity types:   Person, Team, Project, Component, Product, Announcement
Relation types: WORKS_ON, LEADS, MEMBER_OF, BUILDS, DEPENDS_ON, ANNOUNCES
Return [{{"head","head_type","relation","tail","tail_type"}}],
or [] if none.
Text: {chunk}"""

CACHE = json.loads((HERE / "cached_extractions.json").read_text())
stats = {"malformed": [], "rejected": []}


def raw_reply(chunk_id, chunk):
    if config.LLM_PROVIDER == "offline":          # recorded model output
        cached = CACHE.get(chunk_id, [])
        return cached if isinstance(cached, str) else json.dumps(cached)
    return call_llm(PROMPT.format(chunk=chunk))   # LLM/Bedrock/Ollama call


def extract(chunk_id, chunk):
    raw = raw_reply(chunk_id, chunk)
    triples = parse_json(raw)          # tolerant json.loads (fences, prose)
    if triples is None:
        stats["malformed"].append(chunk_id)
        return []                       # skip + log malformed output
    kept = [t for t in triples if t.get("relation") in ALLOWED_RELATIONS]
    stats["rejected"] += [t for t in triples if t not in kept]
    return kept

def load(tx, triples):
    tx.run("""
        UNWIND $triples AS t
        MERGE (h:Entity {name: t.head})  ON CREATE SET h.type = t.head_type
        MERGE (a:Entity {name: t.tail})  ON CREATE SET a.type = t.tail_type
        MERGE (h)-[r:REL {type: t.relation}]->(a)
    """, triples=triples)

def link_chunk(tx, chunk_id, text, triples):
    tx.run("""
        MERGE (c:Chunk {id: $id}) SET c.text = $text
        WITH c
        UNWIND $names AS name
        MATCH (e:Entity {name: name})
        MERGE (c)-[:MENTIONS]->(e)
    """, id=chunk_id, text=text,
         names=sorted({t["head"] for t in triples} | {t["tail"] for t in triples}))

def setup(tx):
    tx.run("CREATE CONSTRAINT e_name IF NOT EXISTS "
           "FOR (e:Entity) REQUIRE e.name IS UNIQUE")
    tx.run("CREATE CONSTRAINT chunk_id IF NOT EXISTS "
           "FOR (c:Chunk) REQUIRE c.id IS UNIQUE")


def main():
    neo.run("DROP CONSTRAINT entity_name IF EXISTS")   # same rule, other labs
    neo.reset(["Entity", "Chunk"])
    n = 0
    with driver.session() as s:
        s.execute_write(setup)              # constraint before load (Ch 7)
        for chunk_id, chunk in load_chunks("examples/athena/corpus/"):
            triples = extract(chunk_id, chunk)
            s.execute_write(load, triples)  # MERGE: idempotent (Ch 7)
            s.execute_write(link_chunk, chunk_id, chunk, triples)
            n += 1
    driver.close()
    counts = neo.run("MATCH (e:Entity) WITH count(e) AS entities "
                     "MATCH ()-[r:REL]->() RETURN entities, count(r) AS rels")[0]
    print(f"Extracted from {n} chunks (LLM_PROVIDER={config.LLM_PROVIDER}): "
          f"{counts['entities']} entities, {counts['rels']} relationships")
    for cid in stats["malformed"]:
        print(f"  ! malformed reply skipped: {cid}")
    for t in stats["rejected"]:
        print(f"  - rejected (relation outside the schema): "
              f"{t.get('head')} {t.get('relation')} {t.get('tail')}")


if __name__ == "__main__":
    main()
