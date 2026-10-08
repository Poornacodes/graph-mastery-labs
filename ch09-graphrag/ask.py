"""Section 9.4, steps 3–4: hybrid retrieval (Listing 9.1) and a grounded,
cited answer (Listing 9.2), compared with a vector-only baseline.

  python ask.py "How is Ben connected to the company Ada founded?"

With LLM_PROVIDER=offline (the default) no model is called: the script prints
the context each approach retrieved, and the graph's connecting path, so you
can see exactly what the graph added. Set LLM_PROVIDER to ollama, anthropic,
or bedrock to also generate answers.
"""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from graphlab import config, embed, neo
from graphlab.llm import call_llm

# Listing 9.1 — Hybrid retrieval in Cypher (vector seed, then graph expansion)
HYBRID = """
// 1. Vector search: the chunks most similar to the question embedding
CALL db.index.vector.queryNodes('chunkEmbedding', 5, $questionVector)
YIELD node AS chunk, score

// 2. Graph expansion: entities mentioned + their 1-2 hop neighborhood
MATCH (chunk)-[:MENTIONS]->(e:Entity)-[:RELATED_TO*1..2]-(context:Entity)
RETURN chunk.text,
       collect(DISTINCT context.name) AS related_context,
       score
ORDER BY score DESC
"""

VECTOR_ONLY = """
CALL db.index.vector.queryNodes('chunkEmbedding', 3, $questionVector)
YIELD node AS chunk, score
RETURN chunk.text, score ORDER BY score DESC
"""

# The relationships among the retrieved entities: the "graph facts" the
# prompt cites (each fact is a node-edge-node triple)
FACTS = """
MATCH (a:Entity)-[r:RELATED_TO]->(b:Entity)
WHERE a.name IN $names AND b.name IN $names
RETURN a.name + ' ' + r.type + ' ' + b.name AS fact
"""

# For the offline answer: every short path between entities in the question
PATHS = """
MATCH (a:Entity {name:$a}), (b:Entity {name:$b})
MATCH p = (a)-[:RELATED_TO*1..4]-(b)
RETURN [r IN relationships(p) |
        startNode(r).name + ' ' + r.type + ' ' + endNode(r).name] AS path
ORDER BY length(p) LIMIT 5
"""

# Listing 9.2 — Grounding prompt (the shape that matters)
PROMPT = """Answer the question using ONLY the provided context.
If the answer is not present, say you do not know.
Cite the specific facts (nodes/edges) you used.

Text context:
{retrieved_chunks}

Graph facts:
{expanded_relationships}

Question: {question}"""


def aliases():
    facts = json.loads((HERE / "facts.json").read_text())
    return {n: [n] + info["aliases"] for n, info in facts["entities"].items()}


def entities_in(text):
    return [n for n, names in aliases().items()
            if any(a in text for a in names)]


def hybrid(question):
    qvec = embed.embed(question)
    rows = neo.run(HYBRID, questionVector=qvec)
    names = sorted({n for r in rows for n in r["related_context"]})
    facts = [r["fact"] for r in neo.run(FACTS, names=names)]
    return rows, facts


def vector_only(question):
    return neo.run(VECTOR_ONLY, questionVector=embed.embed(question))


def main():
    question = " ".join(sys.argv[1:]) or \
        "How is Ben connected to the company Ada founded?"
    print(f"Question: {question}\n")

    base = vector_only(question)
    print("=== Vector-only baseline: retrieved text ===")
    for r in base:
        print(f"  ({r['score']:.2f}) {r['chunk.text'][:110]}")

    rows, facts = hybrid(question)
    print("\n=== GraphRAG: retrieved text ===")
    for r in rows:
        print(f"  ({r['score']:.2f}) {r['chunk.text'][:110]}")
    print("=== GraphRAG: graph facts ===")
    for f in facts:
        print("  -", f)

    # Which graph facts could the baseline not have known? Those linking an
    # entity its text never mentions.
    seen = set(entities_in(" ".join(r["chunk.text"] for r in base)))
    missing = [f for f in facts
               if not all(e in seen for e in entities_in(f))]
    print("\nFacts the vector-only baseline never retrieved:")
    for f in missing:
        print("  -", f)

    ents = entities_in(question)
    if len(ents) >= 2:
        print(f"\nPaths connecting {ents[0]} and {ents[1]} "
              "(each step is a citable edge):")
        for row in neo.run(PATHS, a=ents[0], b=ents[1]):
            print("  * " + "; ".join(row["path"]))
        print("The model gets all of these and picks the one the question asks\n"
              "about. Set LLM_PROVIDER to generate the answers.")

    if config.LLM_PROVIDER != "offline":
        print(f"\n=== Answers ({config.LLM_PROVIDER}) ===")
        base_prompt = PROMPT.format(
            retrieved_chunks="\n".join(r["chunk.text"] for r in base),
            expanded_relationships="(none: vector-only)", question=question)
        graph_prompt = PROMPT.format(
            retrieved_chunks="\n".join(r["chunk.text"] for r in rows),
            expanded_relationships="\n".join(f"- {f}" for f in facts),
            question=question)
        print("Vector-only:", call_llm(base_prompt).strip(), "\n")
        print("GraphRAG:   ", call_llm(graph_prompt).strip())


if __name__ == "__main__":
    main()
