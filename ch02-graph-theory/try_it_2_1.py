"""Try It Yourself 2.1 — check your paper answers.

The four-node directed graph: Alice→Bob, Alice→Carol, Bob→Carol,
Carol→Dave, Dave→Alice. Work it on paper first, then run this.
"""
import networkx as nx

edges = [("Alice", "Bob"), ("Alice", "Carol"), ("Bob", "Carol"),
         ("Carol", "Dave"), ("Dave", "Alice")]
G = nx.DiGraph(edges)
nodes = ["Alice", "Bob", "Carol", "Dave"]

print("Edge list:")
for u, v in edges:
    print(f"  {u} -> {v}")

print("\nAdjacency list:")
for n in nodes:
    print(f"  {n}: {sorted(G.successors(n))}")

print("\nAdjacency matrix (rows = from, columns = to):")
M = nx.to_numpy_array(G, nodelist=nodes, dtype=int)
print("         " + "  ".join(f"{n[:5]:>5}" for n in nodes))
for n, row in zip(nodes, M):
    print(f"  {n:<6} " + "  ".join(f"{int(x):>5}" for x in row))

print("\nDegrees:")
for n in nodes:
    print(f"  {n:<6} in={G.in_degree(n)}  out={G.out_degree(n)}")

print("\nStrongly connected?", nx.is_strongly_connected(G))
print("  (Alice→Carol→Dave→Alice is a cycle, and Bob is reached from Alice\n"
      "   and reaches Carol, so every node can reach every other.)")

print("\nReflection: with a million nodes and a handful of edges each, use an\n"
      "adjacency list (or edge list): O(V+E) space. A matrix would need\n"
      "10^12 cells, almost all zero.")
