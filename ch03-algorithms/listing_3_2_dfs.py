"""Listing 3.2 — Depth-first search from scratch."""


def dfs(graph, start, visited=None, order=None):
    if visited is None:
        visited, order = set(), []
    visited.add(start)
    order.append(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited, order)   # recursion -> depth
    return order


if __name__ == "__main__":
    graph = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"],
             "D": ["B", "C", "E"], "E": ["D"]}
    print("DFS from A:", dfs(graph, "A"))   # A, B, D, C, E
