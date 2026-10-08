"""Listing 8.4 — Contract-testing the API (plus the explainable variant).

Run from ch08-fullstack-app/ with the Chapter 7 data loaded:  pytest -q
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_recos_shape():
    r = client.get("/users/1/recommendations?limit=3")
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        assert len(r.json()["recommendations"]) <= 3

def test_explained_says_why():
    r = client.get("/users/1/recommendations/explained?limit=3")
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        for rec in r.json()["recommendations"]:
            assert rec["because_you_liked"]

def test_graph_endpoint_is_vis_ready():
    d = client.get("/graph/users/1").json()
    ids = {n["id"] for n in d["nodes"]}
    assert all(e["from"] in ids and e["to"] in ids for e in d["edges"])

def test_unknown_user_is_404():
    assert client.get("/users/999999/recommendations").status_code == 404
