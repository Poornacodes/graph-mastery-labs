"""Listing 4.6 — The Python driver, parameterized."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from graphlab import config  # reads NEO4J_URI / NEO4J_PASSWORD (defaults below)

from neo4j import GraphDatabase

driver = GraphDatabase.driver(config.NEO4J_URI,           # bolt://localhost:7687
                              auth=(config.NEO4J_USER,    # neo4j
                                    config.NEO4J_PASSWORD))  # graphmastery

def add_person(tx, name, age):
    tx.run("MERGE (p:Person {name:$name}) SET p.age = $age",
           name=name, age=age)

with driver.session() as s:
    s.execute_write(add_person, "Alice", 30)
    print(s.run("MATCH (p:Person {name:$n}) RETURN p.age AS age",
                n="Alice").single()["age"])
driver.close()
