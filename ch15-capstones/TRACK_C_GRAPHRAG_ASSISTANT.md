# Track C — GraphRAG Knowledge Assistant

A production-shaped GraphRAG assistant over a domain corpus. **Proves:** the
most in-demand skill set, end to end. **Budget:** 15–30 hours.

## Scope suggestion
200–2,000 documents in one domain (product docs, a policy handbook, research
abstracts). Start from `examples/athena/` and `ch09-graphrag/` in this
repository.

## Required
1. **Ingest and embed** chunks into a vector index. Chapter 9.
2. **Build a knowledge graph** linking entities mentioned in the chunks,
   extracted under a closed schema. Chapter 11.
3. **Hybrid retrieval**: vector seeds, then graph expansion (Listing 9.1).
4. **Grounded generation** that cites nodes and paths and says "I don't
   know" when the context lacks the answer (Listing 9.2).
5. **Evaluation** on a gold set of at least 20 questions, at least 8 of them
   multi-hop, comparing GraphRAG with a vector-only baseline on retrieval
   (did the needed facts appear?) and generation (correct and faithful?).
6. **Serve it** behind an API with a page that renders the cited subgraph.

## Acceptance criteria
- [ ] A results table in the shape of Table E.1, from your own gold set.
- [ ] Every answer returns its citations; unanswerable questions abstain.
- [ ] The graph rebuilds from the corpus with one command.
- [ ] Docker Compose stack; README, diagram, demo video.

## Stretch
Deploy on AWS with Bedrock and Neptune Analytics (Chapter 13), or compare
your pipeline with Bedrock Knowledge Bases' managed GraphRAG on the same gold
set.
