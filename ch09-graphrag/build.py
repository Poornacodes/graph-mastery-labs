"""Section 9.4, steps 1–2: chunk and embed the corpus into Neo4j's vector
index, and link (:Chunk)-[:MENTIONS]->(:Entity) plus the entity graph.

  python build.py
"""
import json
import re
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from graphlab import embed, neo


def chunks():
    for doc in sorted((HERE / "corpus").glob("*.txt")):
        for i, para in enumerate(p.strip() for p in doc.read_text().split("\n\n")):
            if para:
                yield {"id": f"{doc.stem}#{i}", "source": doc.name, "text": para}


def mentions(text, facts):
    found = []
    for name, info in facts["entities"].items():
        for alias in [name] + info["aliases"]:
            if re.search(rf"\b{re.escape(alias)}\b", text):
                found.append(name)
                break
    return found


def main():
    facts = json.loads((HERE / "facts.json").read_text())
    rows = list(chunks())
    vectors = embed.embed([r["text"] for r in rows])
    for r, v in zip(rows, vectors):
        r["embedding"] = v
        r["entities"] = mentions(r["text"], facts)

    neo.reset(["Chunk", "Entity"])
    neo.run("DROP INDEX chunkEmbedding IF EXISTS")
    neo.run("CREATE CONSTRAINT entity_name IF NOT EXISTS "
            "FOR (e:Entity) REQUIRE e.name IS UNIQUE")
    neo.run(f"""CREATE VECTOR INDEX chunkEmbedding IF NOT EXISTS
                FOR (c:Chunk) ON c.embedding
                OPTIONS {{indexConfig: {{
                  `vector.dimensions`: {len(vectors[0])},
                  `vector.similarity_function`: 'cosine'}}}}""")
    neo.run("""UNWIND $ents AS e
               MERGE (n:Entity {name: e.name}) SET n.type = e.type""",
            ents=[{"name": k, "type": v["type"]}
                  for k, v in facts["entities"].items()])
    neo.run("""UNWIND $triples AS t
               MATCH (a:Entity {name: t[0]}), (b:Entity {name: t[2]})
               MERGE (a)-[:RELATED_TO {type: t[1]}]->(b)""",
            triples=facts["triples"])
    neo.run("""UNWIND $rows AS r
               MERGE (c:Chunk {id: r.id})
                 SET c.text = r.text, c.source = r.source
               WITH c, r
               CALL db.create.setNodeVectorProperty(c, 'embedding', r.embedding)
               WITH c, r
               UNWIND r.entities AS name
               MATCH (e:Entity {name: name})
               MERGE (c)-[:MENTIONS]->(e)""", rows=rows)
    neo.run("CALL db.awaitIndexes(300)")
    print(f"Loaded {len(rows)} chunks, {len(facts['entities'])} entities, "
          f"{len(facts['triples'])} relationships.")


if __name__ == "__main__":
    main()
