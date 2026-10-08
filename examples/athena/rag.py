"""Section E.7 — Making it GraphRAG: embed every chunk into Neo4j's vector
index, then answer with vector-find + graph-expand (Listing E.5) and a
grounded, cited generation step (Listing E.6).

  python rag.py index
  python rag.py "Who is at risk of losing context now that Dr. Vance left the Orion project?"
"""
import sys

from common import ROOT  # noqa: F401  (sets the import path)
from graphlab import config, embed, neo
from graphlab.llm import call_llm

# Listing E.5 — Hybrid retrieval for Athena
HYBRID_RETRIEVAL = """
CALL db.index.vector.queryNodes('chunkEmbedding', 5, $questionVector)
YIELD node AS chunk, score
MATCH (chunk)-[:MENTIONS]->(e:Entity)-[:REL*1..2]-(context:Entity)
RETURN chunk.text,
       collect(DISTINCT e.name)       AS seed_entities,
       collect(DISTINCT context.name) AS expanded_context,
       score
ORDER BY score DESC
"""

VECTOR_ONLY = """
CALL db.index.vector.queryNodes('chunkEmbedding', 5, $questionVector)
YIELD node AS chunk, score
RETURN chunk.text, score ORDER BY score DESC
"""

# The edges that touch an entity the retrieved chunks mention (the seeds),
# within the expanded neighborhood, so the model can cite each step. On a
# small graph, every edge among all expanded entities would be most of it.
GRAPH_FACTS = """
MATCH (a:Entity)-[r:REL]->(b:Entity)
WHERE (a.name IN $seeds AND b.name IN $names)
   OR (b.name IN $seeds AND a.name IN $names)
RETURN a.name + ' ' + r.type + ' ' + b.name AS fact
"""


def run_cypher(query, **params):
    return neo.run(query, **params)


def index():
    chunks = neo.run("MATCH (c:Chunk) RETURN c.id AS id, c.text AS text")
    vecs = embed.embed([c["text"] for c in chunks])
    neo.run("DROP INDEX chunkEmbedding IF EXISTS")
    neo.run(f"""CREATE VECTOR INDEX chunkEmbedding IF NOT EXISTS
                FOR (c:Chunk) ON c.embedding
                OPTIONS {{indexConfig: {{
                  `vector.dimensions`: {len(vecs[0])},
                  `vector.similarity_function`: 'cosine'}}}}""")
    neo.run("""UNWIND $rows AS r MATCH (c:Chunk {id: r.id})
               CALL db.create.setNodeVectorProperty(c, 'embedding', r.vec)""",
            rows=[{"id": c["id"], "vec": v} for c, v in zip(chunks, vecs)])
    neo.run("CALL db.awaitIndexes(300)")
    print(f"Embedded {len(chunks)} chunks into the chunkEmbedding vector index")


def retrieve(question):
    """GraphRAG context: (rows, graph facts)."""
    qvec = embed.embed(question)
    rows = run_cypher(HYBRID_RETRIEVAL, questionVector=qvec)
    seeds = sorted({n for r in rows for n in r["seed_entities"]})
    names = sorted({n for r in rows for n in r["expanded_context"]} | set(seeds))
    facts = [r["fact"] for r in run_cypher(GRAPH_FACTS, seeds=seeds, names=names)]
    return rows, facts


def retrieve_vector_only(question):
    return run_cypher(VECTOR_ONLY, questionVector=embed.embed(question))


# Listing E.6 — The grounded, cited generation step. (The listing passes the
# expanded entity names as graph context; here each graph fact is a whole
# edge, which gives the model something precise to cite.)
def answer(question):
    rows, facts = retrieve(question)
    text_ctx  = "\n".join(r["chunk.text"] for r in rows)
    graph_ctx = "\n".join(f"- {f}" for f in facts)
    prompt = f"""Answer using ONLY the context.
If the answer is absent, say "I don't know."
Cite the entities/paths you used.
Text: {text_ctx}
Graph facts: {graph_ctx}
Question: {question}"""
    if config.LLM_PROVIDER == "offline":
        return ("(LLM_PROVIDER=offline: no model was called. The grounded "
                "context it would answer from is below.)\n" + graph_ctx), rows
    return call_llm(prompt), rows       # the answer + its citations


if __name__ == "__main__":
    if sys.argv[1:] == ["index"]:
        index()
    else:
        q = " ".join(sys.argv[1:]) or ("Who is at risk of losing context now "
                                       "that Dr. Vance left the Orion project?")
        text, rows = answer(q)
        print("Q:", q, "\n")
        print(text)
        print("\nCited seed entities:", sorted({e for r in rows
                                                for e in r["seed_entities"]}))
