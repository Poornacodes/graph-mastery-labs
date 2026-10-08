"""Listings 3.4–3.6 — centralities, PageRank, and Louvain on the karate club."""
import networkx as nx
import networkx.algorithms.community as nxcom

# Listing 3.4 — Comparing centralities on a real network
G = nx.karate_club_graph()   # 34 members of a club that later split in two

def top(d, k=3):
    return sorted(d.items(), key=lambda kv: -kv[1])[:k]

print("Degree     :", top(nx.degree_centrality(G)))
print("Betweenness:", top(nx.betweenness_centrality(G)))
print("Eigenvector:", top(nx.eigenvector_centrality(G, max_iter=1000)))

# Listing 3.5 — PageRank, global and personalized
pr  = nx.pagerank(G, alpha=0.85)
ppr = nx.pagerank(G, alpha=0.85,
                  personalization={0: 1.0})  # bias toward node 0
print("Global top:",         top(pr, 5))
print("Personalized top:",   top(ppr, 5))

# Listing 3.6 — Community detection with Louvain
G = nx.karate_club_graph()
communities = nxcom.louvain_communities(G, seed=42)
print(f"Found {len(communities)} communities")
print("Modularity:", round(nxcom.modularity(G, communities), 3))
