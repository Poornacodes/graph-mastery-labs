"""Try It Yourself 6.1 — watch facts you never typed appear.

1. Ask "who is a foaf:Person?" -> nothing (never stated).
2. Run an OWL-RL reasoner -> Alice, Bob, Carol appear (worksAt's domain is
   Employee, and Employee is a subclass of Person); colleagueOf runs both
   ways; the ancestorOf chain closes.
3. Add a nameless "ghost" employee and catch it with the SHACL shape.
"""
from pathlib import Path

import owlrl
from pyshacl import validate
from rdflib import Graph

HERE = Path(__file__).resolve().parent
PREFIX = """PREFIX ex: <http://example.org/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
"""


def names(g, where):
    q = PREFIX + f"SELECT DISTINCT ?name WHERE {{ {where} }} ORDER BY ?name"
    return [str(r.name) for r in g.query(q)]


g = Graph().parse(HERE / "try_it_6_1_company.ttl")
persons = "?p a foaf:Person ; foaf:name ?name ."
print("1. Persons before reasoning:", names(g, persons) or "(none)")

owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
print("2. Persons after reasoning: ", names(g, persons))
print("   Bob's colleagues (inferred, symmetric):",
      names(g, "ex:bob ex:colleagueOf ?c . ?c foaf:name ?name ."))
print("   Dora's descendants (inferred, transitive):",
      names(g, "ex:dora ex:ancestorOf ?d . ?d foaf:name ?name ."))

g.parse(data="""@prefix ex: <http://example.org/> .
ex:ghost ex:worksAt ex:acme .""", format="turtle")   # no name
owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
conforms, _, report = validate(
    g, shacl_graph=str(HERE / "listing_6_4_shacl.ttl"))
print("3. SHACL conforms with the ghost added:", conforms)
for line in report.splitlines():
    if "Focus Node" in line or "Message" in line:
        print("  ", line.strip())
assert not conforms
