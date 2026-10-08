# Track B — Fraud / Anomaly Detection System

Detect suspicious patterns where the relationships are the signal: shared
devices, shared addresses, transfer chains. **Proves:** modeling for
detection, GDS algorithms at scale, explainable flagging. **Budget:** 15–30
hours.

## Scope suggestion
Generate a synthetic dataset (you control the ground truth): 5,000–50,000
accounts, devices, addresses, and transfers, with a few planted rings
(accounts sharing devices and moving money in cycles) and some mules
(accounts that bridge rings). Public alternatives: the PaySim or IEEE-CIS
fraud datasets, remodeled as a graph.

## Required
1. **Model** accounts, devices, addresses, and transfers so that "shares a
   device with" and "sent money to" are single hops. Chapter 7.
2. **Community detection** (Louvain or WCC) to surface rings. Chapters 3–4.
3. **Centrality** (betweenness or PageRank) to find brokers and mules.
4. **Variable-length path queries** that find transfer cycles of length 3–6.
5. **An explainable risk score** per account, served by an API together
   with the evidence subgraph, and visualized. Chapter 8.

## Acceptance criteria
- [ ] Precision and recall against your planted ground truth, reported.
- [ ] Each flagged account returns *why*: the ring, the shared devices, the
      cycle.
- [ ] GDS projections are created and dropped cleanly; algorithm runs are
      timed and reported at your data size.
- [ ] Idempotent loader; contract tests on the API.
- [ ] README, model diagram, demo video.

## Stretch
Train a link-prediction or node-classification model on graph features
(Chapter 10) and compare it with the rule-based score.
