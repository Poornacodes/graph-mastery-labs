"""Try It Yourself 13.1, no-cost path: the Listing 13.1 queries against local
stand-ins for Neptune — openCypher on Neo4j, Gremlin on JanusGraph, SPARQL on
Fuseki — then the local-to-AWS mapping (ARCHITECTURE.md).

  docker compose --profile gremlin up -d     # from the repository root
  python try_it_13_1_local.py
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ch05-query-languages"))
from graphlab import config, neo

# openCypher (the Listing 13.1 query, unchanged) on Neo4j
neo.run("MATCH (p:Person) WHERE p.name IN ['Alice','Bob','Carol','Dave'] "
        "DETACH DELETE p")
neo.run_file(ROOT / "ch05-query-languages" / "knows.cypher")
rows = neo.run("MATCH (:Person {name:'Alice'})-[:KNOWS]->(f:Person) "
               "RETURN f.name AS friend")
print("openCypher (Neo4j):   ", sorted(r["friend"] for r in rows))

# Gremlin on JanusGraph
try:
    import gremlin_lab
    print("Gremlin (JanusGraph): ", gremlin_lab.run_5_2()["direct"])
except Exception as exc:
    print(f"Gremlin (JanusGraph):  skipped ({type(exc).__name__}); start it with "
          "`docker compose --profile gremlin up -d`")

# SPARQL on Fuseki: create an in-memory dataset, upload the triples, query
QUERY = """PREFIX ex: <http://example.org/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name WHERE { ex:alice foaf:knows ?f . ?f foaf:name ?name . }"""
try:
    import base64
    import urllib.parse
    import urllib.request
    import os
    auth = "Basic " + base64.b64encode(
        f"admin:{os.getenv('FUSEKI_PASSWORD', 'graphmastery')}".encode()).decode()
    def call(method, path, data=None, ctype=None):
        req = urllib.request.Request(config.FUSEKI_URL + path, data=data,
                                     method=method)
        req.add_header("Authorization", auth)
        if ctype:
            req.add_header("Content-Type", ctype)
        return urllib.request.urlopen(req, timeout=10)
    try:
        call("POST", "/$/datasets",
             urllib.parse.urlencode({"dbName": "gm", "dbType": "mem"}).encode(),
             "application/x-www-form-urlencoded")
    except urllib.error.HTTPError as e:
        if e.code != 409:          # 409: dataset already exists
            raise
    call("PUT", "/gm/data",
         (ROOT / "ch05-query-languages" / "knows.ttl").read_bytes(), "text/turtle")
    from SPARQLWrapper import JSON, SPARQLWrapper
    sw = SPARQLWrapper(config.FUSEKI_URL + "/gm/sparql")
    sw.setQuery(QUERY)
    sw.setReturnFormat(JSON)
    res = sw.query().convert()
    print("SPARQL (Fuseki):      ",
          sorted(b["name"]["value"] for b in res["results"]["bindings"]))
except Exception as exc:
    print(f"SPARQL (Fuseki):       skipped ({type(exc).__name__}: {exc})")

print("\nThe same three queries run unchanged in a Neptune notebook "
      "(neptune_notebook.ipynb).")
print("Local components and their AWS services: see ARCHITECTURE.md.")
