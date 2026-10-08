"""Listing 10.2 — Link prediction from classic features, completed into the
Try It Yourself 10.1 experiment: hide some edges of a
community-structured graph, then predict them from the structure that
remains, against random non-edges. AUC 0.5 is chance; 1.0 is perfect."""
import random

import networkx as nx
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

def features(g, u, v):
    cn  = len(list(nx.common_neighbors(g, u, v)))
    jac = next(nx.jaccard_coefficient(g, [(u, v)]))[2]
    aa  = next(nx.adamic_adar_index(g, [(u, v)]))[2] if cn else 0.0
    pa  = next(nx.preferential_attachment(g, [(u, v)]))[2]
    return [cn, jac, aa, pa]

# A community-structured graph: dense inside 8 groups, sparse between them
rnd = random.Random(42)
G = nx.planted_partition_graph(8, 25, p_in=0.4, p_out=0.01, seed=42)

# Hide two disjoint 15% slices of the edges: one to train on, one to test on.
# Both are featurized on the graph that remains, so the model never sees the
# edge it is asked to predict.
edges = list(G.edges())
rnd.shuffle(edges)
k = int(len(edges) * 0.15)
train_pos, test_pos = edges[:k], edges[k:2 * k]
observed = G.copy()
observed.remove_edges_from(train_pos + test_pos)

def non_edges(k):
    nodes, out = list(G), set()
    while len(out) < k:
        u, v = rnd.sample(nodes, 2)
        if not G.has_edge(u, v):
            out.add((u, v))
    return list(out)

negatives = non_edges(2 * k)
train_neg, test_neg = negatives[:k], negatives[k:]
X = [features(observed, u, v) for u, v in train_pos + train_neg]
y = [1] * len(train_pos) + [0] * len(train_neg)
X_test = [features(observed, u, v) for u, v in test_pos + test_neg]
y_test = [1] * len(test_pos) + [0] * len(test_neg)

clf = LogisticRegression(max_iter=1000).fit(X, y)
auc = roc_auc_score(y_test, clf.predict_proba(X_test)[:, 1])
print(f"Held-out link-prediction AUC: {auc:.3f}  (chance = 0.5)")
print("Why it works: triadic closure — two nodes with many common neighbors\n"
      "are likely to be (or become) connected, especially inside a community.")
assert auc > 0.7
