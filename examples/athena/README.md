# Athena — the Appendix E worked example

Athena is an internal knowledge assistant for the fictional *Helios
Robotics*. It answers questions over the company's documents with grounded,
cited, multi-hop answers. This folder is the runnable version of Appendix E.

## Run it

From the repository root, with the lab stack up (`docker compose up -d`) and
dependencies installed:

```bash
cd examples/athena
python run_all.py          # every step, in order
uvicorn api:app --reload   # then open http://localhost:8000/
```

Everything runs with no LLM (`LLM_PROVIDER=offline`, the default): extraction
replays `cached_extractions.json`, the model output recorded for each chunk,
and answers show the grounded context the model would answer from. Set
`LLM_PROVIDER=ollama`, `anthropic`, or `bedrock` (see `.env.example` at the
repository root) to extract and answer with a real model.

## The steps

| Section | Script | What it shows |
|---|---|---|
| E.2 | `ontology.ttl` | Listing E.1: six classes, six relations, `dependsOn` transitive |
| E.3 | `extract.py` | Listing E.2: closed-schema extraction, defensive parsing (one reply is prose, not JSON, and is skipped), out-of-schema relations rejected, idempotent `MERGE` |
| E.4 | `resolve.py` | "R. Okafor", "Okafor" → "Rina Okafor"; "Dr. Vance" → "Elena Vance"; "Orion" → "Project Orion"; merged with Listing E.3's `apoc.refactor.mergeNodes` |
| E.5 | `reason.py`, `shapes.ttl` | An RDF twin with no asserted types: the reasoner infers them and closes `dependsOn` chains; SHACL checks names and single leads |
| E.6 | `questions.cypher`, `questions.py` | Listing E.4's four competency questions, then PageRank and Louvain in GDS |
| E.7 | `rag.py` | Chunks embedded into the `chunkEmbedding` vector index; Listing E.5 hybrid retrieval; Listing E.6 grounded, cited generation |
| E.8 | `api.py`, `static/index.html` | Listing E.7: `/ask` and `/graph/entity/{name}`, with a vis-network page |
| E.9 | `evaluate.py`, `gold.json` | 20 gold questions (8 multi-hop), GraphRAG vs vector-only; writes `results.md` |
| E.10 | `Dockerfile`, `docker-compose.yml` | The API and Neo4j as a Compose stack |

## Results on this corpus

Offline, with the default embedding model, retrieval (did the facts needed
for the answer reach the model's context?) comes out:

| Question type | Vector-only | GraphRAG (Athena) |
|---|---|---|
| Single-fact (12) | 12 / 12 | 12 / 12 |
| Multi-hop (8) | 4 / 8 | 8 / 8 |
| **Total (20)** | **16 / 20** | **20 / 20** |

The same shape as Table E.1: parity on single-fact questions, a decisive
GraphRAG advantage on multi-hop. With an LLM configured, `evaluate.py` also
scores the generated answers.

The corpus here is 20 short documents rather than Appendix E's ~200, so the
whole pipeline runs quickly on a laptop.

## Try It Yourself E.1 — your own corpus

1. Replace `corpus/` with your own small corpus (a team wiki export, a set of
   README files), one `.txt` file per document, paragraphs separated by a
   blank line.
2. Set `LLM_PROVIDER` to a real model (the cached extractions only cover the
   Helios corpus).
3. Edit the entity and relation types in `extract.py`'s `PROMPT` and
   `ALLOWED_RELATIONS`, and the ontology and shapes to match your domain.
4. Write five competency questions and a gold set in `gold.json`, then run
   `python run_all.py` and compare your table with the one above.

If GraphRAG does not beat the baseline on your multi-hop questions, inspect
entity resolution first (`resolve.py` prints what it merged and a review
queue of similar names it did not): split entities are the usual culprit.
