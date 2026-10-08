# Track A — Knowledge Graph Platform

Build a knowledge graph from documents that reasons and answers with cited
evidence. **Proves:** ontology engineering, knowledge-graph construction,
reasoning, GraphRAG. **Budget:** 15–30 hours.

## Scope suggestion
Pick a domain with 50–300 short documents you can legally use: your team's
wiki export, a set of open-source project READMEs, public company press
releases, or a Wikipedia category. Write five competency questions first,
at least two of them multi-hop.

## Required
1. **Ontology** (Turtle) with domain/range on every property and at least two
   OWL characteristics used for real (transitive, symmetric, inverse,
   disjoint). Chapter 6.
2. **Extraction**, LLM-driven or rule-based, under a closed schema, with
   defensive parsing and a log of rejected output. Chapter 11.
3. **Entity resolution** with a measured before/after: how many duplicate
   clusters you merged. Section 11.4.
4. **Reasoning** that materializes at least one class of fact nobody typed
   (show a query that returns nothing before and something after).
5. **SHACL validation** run in the pipeline; the build fails on violations.
6. **A GraphRAG Q&A endpoint** returning the answer plus the cited path.
   Chapter 9.

## Acceptance criteria
- [ ] The five competency questions answer correctly from a clean rebuild.
- [ ] Re-running the pipeline produces identical node and edge counts.
- [ ] Inferred facts are distinguishable from asserted ones.
- [ ] SHACL report is clean, and a deliberately broken input is caught.
- [ ] Every answer cites node IDs or a path.
- [ ] README, model diagram, 3–5 minute demo video.

## Stretch
Link entities to Wikidata with `owl:sameAs` and enrich them with a federated
query (Listing 5.4).

`examples/athena/` is a worked version of most of this track.
