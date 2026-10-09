"""Try It Yourself 3.1 — the karate-club lab.

Computes all four centralities and Louvain communities, renders Figure 3.7
to karate.png, and finds the brokers: high betweenness, low degree.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import networkx.algorithms.community as nxcom

G = nx.karate_club_graph()
degree = nx.degree_centrality(G)
between = nx.betweenness_centrality(G)
close = nx.closeness_centrality(G)
eigen = nx.eigenvector_centrality(G, max_iter=1000)
pr = nx.pagerank(G, alpha=0.85)
communities = nxcom.louvain_communities(G, seed=42)
community_of = {n: i for i, c in enumerate(communities) for n in c}

print(f"{'node':>4} {'degree':>7} {'between':>8} {'close':>6} "
      f"{'eigen':>6} {'pagerank':>8} {'comm':>4}")
for n in sorted(G, key=lambda n: -pr[n])[:10]:
    print(f"{n:>4} {degree[n]:7.3f} {between[n]:8.3f} {close[n]:6.3f} "
          f"{eigen[n]:6.3f} {pr[n]:8.3f} {community_of[n]:>4}")

# Brokers: the highest betweenness among nodes with a modest degree (at most
# the average plus a half), so the hubs 0 and 33 are excluded
avg = sum(d for _, d in G.degree()) / G.number_of_nodes()
modest = [n for n in G if G.degree(n) <= 1.5 * avg]
brokers = sorted(modest, key=lambda n: -between[n])[:3]
print(f"\nBrokers (high betweenness, degree <= {1.5 * avg:.1f}):")
for n in brokers:
    print(f"  node {n}: degree {G.degree(n)}, betweenness {between[n]:.3f}")
print("A broker has few connections, but they link otherwise-separate\n"
      "groups, so removing it fragments the network.")

# Figure 3.7: shade by community, size by PageRank
pos = nx.spring_layout(G, seed=7)
shades = ["#222222", "#777777", "#bbbbbb", "#eeeeee"]
plt.figure(figsize=(6, 5))
nx.draw_networkx_edges(G, pos, alpha=0.4)
nx.draw_networkx_nodes(
    G, pos, node_size=[4000 * pr[n] for n in G],
    node_color=[shades[community_of[n] % len(shades)] for n in G],
    edgecolors="black")
nx.draw_networkx_labels(G, pos, font_size=7, font_color="red")
plt.axis("off")
plt.title(f"Karate club: {len(communities)} Louvain communities, "
          "size = PageRank")
out = Path(__file__).with_name("karate.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nFigure written to {out}")
