"""Small conveniences over the Neo4j driver used across the labs."""
from __future__ import annotations

from pathlib import Path

from . import config


def run(query: str, **params) -> list[dict]:
    """Run one query and return its rows as dicts."""
    with config.driver() as drv:
        records, _, _ = drv.execute_query(query, params)
        return [r.data() for r in records]


def run_file(path: str | Path, **params) -> list[list[dict]]:
    """Run every statement in a .cypher file (split on ';' at line ends),
    returning each statement's rows. Lines starting with // are comments."""
    text = Path(path).read_text()
    statements, current = [], []
    for line in text.splitlines():
        current.append(line)
        if line.rstrip().endswith(";"):
            statements.append("\n".join(current).rstrip().rstrip(";"))
            current = []
    if "\n".join(current).strip():
        statements.append("\n".join(current))
    results = []
    with config.driver() as drv:
        for st in statements:
            body = "\n".join(l for l in st.splitlines()
                             if not l.strip().startswith("//")).strip()
            if body:
                records, _, _ = drv.execute_query(body, params)
                results.append([r.data() for r in records])
    return results


def reset(labels: list[str]) -> None:
    """Delete all nodes with the given labels (each lab cleans up after itself
    so labs can share one database)."""
    for label in labels:
        run(f"MATCH (n:`{label}`) DETACH DELETE n")   # lab data is small
