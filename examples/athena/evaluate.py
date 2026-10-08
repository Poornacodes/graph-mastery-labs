"""Section E.9 — Evaluate Athena against a vector-only baseline (Table E.1).

Retrieval (always): a question counts as retrieved when every expected
answer appears in the context the approach would hand the model: the top-5
chunks for vector-only; those chunks plus the graph facts for GraphRAG.
Generation (with an LLM configured): the answer must contain every expected
answer and be grounded in that context.

  python evaluate.py            # writes results.md
"""
import json
from collections import Counter

from common import HERE
from graphlab import config
from graphlab.llm import call_llm
from rag import answer, retrieve, retrieve_vector_only

BASELINE_PROMPT = """Answer using ONLY the context.
If the answer is absent, say "I don't know."
Text: {text}
Question: {question}"""


def hit(expected, text):
    return all(e.lower() in text.lower() for e in expected)


def main():
    gold = json.loads((HERE / "gold.json").read_text())
    use_llm = config.LLM_PROVIDER != "offline"
    score = Counter()
    totals = Counter(g["type"] for g in gold)
    misses = []
    for g in gold:
        q, exp, kind = g["question"], g["expected"], g["type"]
        base_rows = retrieve_vector_only(q)
        base_ctx = "\n".join(r["chunk.text"] for r in base_rows)
        rows, facts = retrieve(q)
        graph_ctx = "\n".join(r["chunk.text"] for r in rows) + "\n" + "\n".join(facts)
        score[(kind, "vector", "retrieval")] += hit(exp, base_ctx)
        score[(kind, "graph", "retrieval")] += hit(exp, graph_ctx)
        if not hit(exp, graph_ctx):
            misses.append(q)
        if use_llm:
            base_answer = call_llm(BASELINE_PROMPT.format(text=base_ctx, question=q))
            graph_answer, _ = answer(q)
            score[(kind, "vector", "generation")] += hit(exp, base_answer)
            score[(kind, "graph", "generation")] += hit(exp, graph_answer)

    stages = ["retrieval"] + (["generation"] if use_llm else [])
    lines = []
    for stage in stages:
        lines += [f"\n### {stage.capitalize()}: needed facts "
                  f"{'present in the context' if stage == 'retrieval' else 'in a correct answer'}\n",
                  "| Question type | Vector-only correct | GraphRAG (Athena) correct |",
                  "|---|---|---|"]
        tv = tg = 0
        for kind in ("single-fact", "multi-hop"):
            v, gr = score[(kind, "vector", stage)], score[(kind, "graph", stage)]
            tv, tg = tv + v, tg + gr
            lines.append(f"| {kind.capitalize()} ({totals[kind]}) | "
                         f"{v} / {totals[kind]} | {gr} / {totals[kind]} |")
        n = len(gold)
        lines.append(f"| **Total ({n})** | **{tv} / {n}** | **{tg} / {n}** |")
    header = (f"# Athena evaluation (LLM_PROVIDER={config.LLM_PROVIDER}, "
              f"EMBED_MODEL={config.EMBED_MODEL})\n")
    if not use_llm:
        header += ("\nOffline run: retrieval only. Set LLM_PROVIDER to score "
                   "generated answers too.\n")
    if misses:
        header += "\nGraphRAG retrieval missed: " + "; ".join(misses) + "\n"
    report = header + "\n".join(lines) + "\n"
    (HERE / "results.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
