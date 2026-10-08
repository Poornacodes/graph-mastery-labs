"""Listing 3.3 — Weighted shortest path with NetworkX."""
import networkx as nx

G = nx.DiGraph()
G.add_weighted_edges_from([
    ("A","B",4), ("A","C",1), ("C","B",1), ("B","D",1), ("C","D",5),
])
print(nx.dijkstra_path(G, "A", "D"))          # ['A','C','B','D']
print(nx.dijkstra_path_length(G, "A", "D"))   # 3 (A->C->D costs 6)
