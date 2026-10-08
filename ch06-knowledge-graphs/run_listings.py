"""Listings 6.1–6.4: load facts + schema, reason, validate."""
from pathlib import Path

import owlrl
from pyshacl import validate
from rdflib import Graph

HERE = Path(__file__).resolve().parent
g = Graph()
for f in ("listing_6_1_facts.ttl", "listing_6_2_rdfs.ttl"):
    g.parse(HERE / f)
print("Triples before reasoning:", len(g))

ask = """PREFIX ex: <http://example.org/>
SELECT ?type WHERE { ex:alice a ?type } ORDER BY ?type"""
print("Alice's types (asserted):", [str(r.type) for r in g.query(ask)])

owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(g)
types = [str(r.type) for r in g.query(ask)
         if str(r.type).startswith(("http://example.org", "http://xmlns"))]
print("Alice's types (after RDFS):", types)   # + ex:Employee via worksAt domain

conforms, _, report = validate(g, shacl_graph=str(HERE / "listing_6_4_shacl.ttl"))
print("SHACL conforms:", conforms)
