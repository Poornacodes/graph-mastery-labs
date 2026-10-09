# Capstone rubric (full version of Table 15.2)

Score each of the seven categories from 1 to 4. **Elite** means a total of at
least 24 of 28 (85%) **and** no category below 3 (Proficient).

| Score | Level | Meaning |
|---|---|---|
| 1 | Novice | Present but ad hoc, or missing |
| 2 | Developing | Works, with clear gaps |
| 3 | Proficient | Sound and complete for the scope |
| 4 | Elite | Exemplary; shows judgment beyond the requirement |

## 1. Data model

| Score | Evidence |
|---|---|
| 1 | Labels and relationships chosen ad hoc; anti-patterns present (god-nodes, JSON blobs on nodes, rich edges that should be nodes) |
| 2 | A reasonable model, but some queries need awkward workarounds |
| 3 | Modeled for your queries: each competency question maps to a direct traversal; constraints on every key |
| 4 | Elegant: intermediate nodes where relationships carry data, a documented diagram, and a short written rationale for each non-obvious choice (LPG vs RDF, what is a node vs a property) |

## 2. Query and analytics

| Score | Evidence |
|---|---|
| 1 | Basic single-hop reads |
| 2 | Multi-hop queries that work but scan labels |
| 3 | Correct multi-hop queries anchored on indexes; `PROFILE` shows index seeks |
| 4 | Advanced patterns (variable-length, shortest paths, aggregation pipelines) plus GDS algorithms or reasoning, each justified, with profiles for the important queries |

## 3. Data pipeline

| Score | Evidence |
|---|---|
| 1 | Data entered by hand |
| 2 | A script loads data once |
| 3 | Scripted ETL with constraints created before load |
| 4 | Idempotent (`MERGE`), batched (`UNWIND`), re-runnable from a clean or existing database with identical counts, and tested for that |

## 4. Application layer

| Score | Evidence |
|---|---|
| 1 | None |
| 2 | Queries run from a notebook or script only |
| 3 | A working API or visualization with parameterized queries and one pooled driver |
| 4 | A clean API and a visualization, contract-tested, with input validation and capped result sizes |

## 5. AI integration

| Score | Evidence |
|---|---|
| 1 | None |
| 2 | Vector retrieval *or* graph retrieval works on a few examples |
| 3 | Hybrid retrieval with grounded answers that cite nodes or paths |
| 4 | Grounded GraphRAG with citations **and** an evaluation on a gold set (including multi-hop questions) against a vector-only baseline, with the results reported |

## 6. Deployment and operations

| Score | Evidence |
|---|---|
| 1 | Runs only on your laptop, by hand |
| 2 | Dockerfile for one component |
| 3 | Docker Compose brings up the whole stack with one command |
| 4 | Compose plus a cloud deployment, versioned schema migrations, and a written monitoring and backup plan with RPO/RTO targets |

## 7. Documentation and communication

| Score | Evidence |
|---|---|
| 1 | Sparse or missing README |
| 2 | README explains how to run it |
| 3 | Clear README: problem, model diagram, how to run, results |
| 4 | README with diagram, a 3–5 minute demo video, design rationale, limitations, and what you would do next |

## Score sheet

| Category | Score (1–4) | Evidence (link to file, test, or video timestamp) |
|---|---|---|
| Data model | | |
| Query and analytics | | |
| Data pipeline | | |
| Application layer | | |
| AI integration | | |
| Deployment and operations | | |
| Documentation | | |
| **Total (of 28)** | | Elite: ≥ 24 and nothing below 3 |
