"""Section E.5 — Reasoning and validation, on an RDF twin of the graph.

Exports the property graph to RDF using the Listing E.1 ontology, *without*
asserting any types, then runs an OWL-RL reasoner: types are inferred from
domain/range, and the transitive dependsOn chains close. SHACL (shapes.ttl)
then checks every Person has a name and every Project at most one lead.
"""
import re

import owlrl
from pyshacl import validate
from rdflib import Graph, Literal, Namespace, RDFS

from common import HERE
from graphlab import neo

EX = Namespace("http://helios.example/")
PREDICATE = {"WORKS_ON": EX.worksOn, "LEADS": EX.leads,
             "MEMBER_OF": EX.memberOf, "BUILDS": EX.builds,
             "DEPENDS_ON": EX.dependsOn, "ANNOUNCES": EX.announces}


def iri(name):
    return EX[re.sub(r"\W+", "_", name).strip("_")]


def rdf_twin():
    g = Graph().parse(HERE / "ontology.ttl")
    for r in neo.run("MATCH (e:Entity) RETURN e.name AS name"):
        g.add((iri(r["name"]), RDFS.label, Literal(r["name"])))
    for r in neo.run("MATCH (a:Entity)-[r:REL]->(b:Entity) "
                     "RETURN a.name AS a, r.type AS t, b.name AS b"):
        g.add((iri(r["a"]), PREDICATE[r["t"]], iri(r["b"])))
    return g


def main():
    g = rdf_twin()
    q = lambda s: [str(x[0]).split("/")[-1] for x in g.query(
        "PREFIX ex: <http://helios.example/>\n" + s)]
    before = q("SELECT ?c WHERE { ex:Project_Orion ex:dependsOn ?c } ORDER BY ?c")
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    after = q("SELECT ?c WHERE { ex:Project_Orion ex:dependsOn ?c } ORDER BY ?c")
    print("Project Orion depends on (asserted):", before)
    print("Project Orion depends on (inferred, transitive):", after)
    print("Inferred Persons:", q("SELECT ?p WHERE { ?p a ex:Person } ORDER BY ?p"))
    print("Inferred Components:",
          q("SELECT ?c WHERE { ?c a ex:Component } ORDER BY ?c"))
    clash = q("SELECT ?x WHERE { ?x a ex:Person, ex:Team }")
    print("Person/Team contradictions:", clash or "none")
    conforms, _, report = validate(g, shacl_graph=str(HERE / "shapes.ttl"))
    print("SHACL conforms:", conforms)
    if not conforms:
        print(report)
    return conforms and not clash


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
