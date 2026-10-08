"""Listing 7.1 — An idempotent, batched loader.

Run from this folder after generate_ratings.py. Also loads product names
(load_products), which the Chapter 8 API returns alongside each product.
"""
import csv
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from graphlab import config

from neo4j import GraphDatabase

driver = GraphDatabase.driver(config.NEO4J_URI,
                              auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))

def setup(tx):
    tx.run("CREATE CONSTRAINT u_id IF NOT EXISTS "
           "FOR (u:User) REQUIRE u.id IS UNIQUE")
    tx.run("CREATE CONSTRAINT p_id IF NOT EXISTS "
           "FOR (p:Product) REQUIRE p.id IS UNIQUE")

def load_ratings(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MERGE (u:User {id: toInteger(row.user_id)})
        MERGE (p:Product {id: toInteger(row.product_id)})
        MERGE (u)-[r:RATED]->(p)
          SET r.stars = toInteger(row.stars)
    """, rows=rows)

def load_products(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MERGE (p:Product {id: toInteger(row.product_id)})
          SET p.name = row.name, p.category = row.category
    """, rows=rows)

def batches(path, size=500):
    with open(path) as f:
        batch = []
        for row in csv.DictReader(f):
            batch.append(row)
            if len(batch) >= size:
                yield batch
                batch = []
        if batch:
            yield batch

DATA = Path(__file__).with_name("data")

if __name__ == "__main__":
    with driver.session() as s:
        s.execute_write(setup)
        for b in batches(DATA / "products.csv"):
            s.execute_write(load_products, b)
        for b in batches(DATA / "ratings.csv"):
            s.execute_write(load_ratings, b)
    driver.close()
    print("Loaded", DATA / "ratings.csv")
