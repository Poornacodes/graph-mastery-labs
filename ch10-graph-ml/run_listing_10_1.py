"""Listing 10.1 on the Chapter 7 ratings graph (load it first with
ch07-modeling-etl/try_it_7_1.py). Writes a 64-dim node2vec embedding to every
User and Product, then shows the products most similar to product 1."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from graphlab import neo

neo.run("CALL gds.graph.exists('myGraph') YIELD exists WITH exists "
        "WHERE exists CALL gds.graph.drop('myGraph') YIELD graphName "
        "RETURN graphName")
neo.run("CALL gds.graph.project('myGraph', ['User','Product'], "
        "{RATED: {orientation: 'UNDIRECTED'}})")
print(neo.run_file(HERE / "listing_10_1_node2vec.cypher")[0])
rows = neo.run("""
    MATCH (a:Product {id: 1}), (b:Product) WHERE b <> a
    RETURN b.name AS product, b.category AS category,
           round(gds.similarity.cosine(a.embedding, b.embedding), 3) AS sim
    ORDER BY sim DESC LIMIT 5""")
first = neo.run("MATCH (p:Product {id:1}) RETURN p.name AS n, p.category AS c")[0]
print(f"Most similar to {first['n']} ({first['c']}):")
for r in rows:
    print("  ", r)
neo.run("CALL gds.graph.drop('myGraph')")
