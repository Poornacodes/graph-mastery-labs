# Interview question bank

Grouped by the themes in Section 15.5. Practice out loud; for design
questions, state the queries you need before you draw the model. The chapter
references point to where the book covers each answer.

## Modeling (Chapters 1, 7)
1. Model a ride-sharing app as a graph. What are your nodes, relationships, and the three queries that drove the design?
2. When should a relationship become a node? Give an example (hint: a relationship that needs its own relationships, such as an employment with a role and a manager).
3. What is a god-node, why does it hurt traversals, and how do you fix one?
4. Your product team wants to store a JSON blob of preferences on each user node. What do you say?
5. How would you model time-varying relationships (who was manager *when*)?
6. Design a schema for a recommendation engine and write its core query.

## Why graphs / why not SQL (Chapter 4)
7. Explain index-free adjacency to a relational-database expert.
8. Why does a five-hop query's cost not grow with total data size in a native graph store?
9. "Why not just use PostgreSQL for our social features?" Answer in three sentences.
10. Give two signals a problem suits a graph database and one signal it does not.

## Representations, complexity, traversal (Chapters 2–3)
11. Adjacency list versus matrix: space, edge lookup, neighbor iteration. When does each win?
12. BFS versus DFS: data structure, guarantees, and a use case for each.
13. Why does Dijkstra fail with negative weights, and what do you use instead?
14. What makes A* faster than Dijkstra, and what must be true of its heuristic?
15. How do you detect a cycle in a directed graph?
16. What is a topological sort and where would you use one?

## Algorithms and centrality (Chapter 3)
17. Degree, betweenness, closeness, eigenvector, PageRank: which answers "who is a broker?", "who is influential?", "who can reach everyone fastest?"
18. Explain PageRank's damping factor and what personalized PageRank changes.
19. What does modularity measure? Why might Louvain return different communities on two runs?
20. A node has high betweenness but low degree. What role does it play in the network?

## Query languages (Chapters 4, 5, 8)
21. Write a Cypher query for friends-of-friends who are not already friends, ranked by mutual friends.
22. `MERGE` versus `CREATE`: what happens on a second run of each?
23. What does `WITH` do in Cypher, and why do you need it for filtering on aggregates?
24. Translate a Cypher friend-of-friend query to Gremlin and to SPARQL.
25. What is GQL, and how does it relate to Cypher?
26. A query's `PROFILE` shows `NodeByLabelScan`. What do you change?

## RDF, ontologies, reasoning (Chapters 2, 6)
27. RDF versus property graph: how does each attach data to a relationship?
28. What is the Open World Assumption, and why does it make "not stated" different from "false"?
29. SHACL versus OWL: which validates, which infers, and why do you often need both?
30. Give an example where reasoning materializes a fact nobody typed.
31. What does `owl:sameAs` let you do, and what is the risk of overusing it?

## GraphRAG and graph ML (Chapters 9–11)
32. Design a GraphRAG system for 10,000 internal documents. Walk through ingest, retrieval, generation, and evaluation.
33. Exactly how does GraphRAG beat vector RAG on a multi-hop question? Give a concrete example.
34. How do you evaluate a RAG system? Separate retrieval metrics from generation metrics.
35. How do you stop an LLM from inventing relationship types during extraction?
36. Your LLM-built graph has "R. Okafor", "Rina Okafor", and "Okafor" as three nodes. What breaks, and how do you fix it?
37. node2vec versus a GNN: when is each the right tool?
38. Why do common-neighbor features predict links? (Triadic closure.)

## Production and cloud (Chapters 12–13)
39. Define RPO and RTO and choose them for a fraud-detection service.
40. How does a Neo4j cluster or Neptune scale reads, and what does it do about writes?
41. How do you migrate a graph schema with zero downtime? (Expand, migrate, contract; idempotent migrations.)
42. Neptune Database versus Neptune Analytics: what is each for?
43. What would you monitor for a graph-backed API, and what would you alert on?
44. How do you keep a cloud lab from running up a bill?

## Behavioral
45. Tell me about a graph project: problem → model → key query or algorithm → result → what you would do next (two minutes).
46. Tell me about a time a model or query you designed was wrong. How did you find out, and what did you change?
