"""Listing 3.1 — Breadth-first search from scratch."""
from collections import deque


def bfs(graph, start):            # graph: dict of node -> list of neighbors
    visited, order, q = {start}, [], deque([start])
    while q:
        node = q.popleft()        # FIFO -> breadth
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                q.append(neighbor)
    return order


if __name__ == "__main__":
    # The five-node graph of Figure 3.1
    graph = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"],
             "D": ["B", "C", "E"], "E": ["D"]}
    print("BFS from A:", bfs(graph, "A"))   # A, B, C, D, E
