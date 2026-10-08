"""Settings for every lab, read from the environment (or a .env file at the
repository root). Defaults match Appendix A of the book."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv(path: Path = ROOT / ".env") -> None:
    """Minimal .env reader (KEY=VALUE lines) so no extra package is needed.
    Real environment variables always win."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "graphmastery")

FUSEKI_URL = os.getenv("FUSEKI_URL", "http://localhost:3030")
GREMLIN_URL = os.getenv("GREMLIN_URL", "ws://localhost:8182/gremlin")

# LLM: offline | ollama | anthropic | bedrock   (see graphlab/llm.py)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "offline")
LLM_MODEL = os.getenv("LLM_MODEL", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Embeddings: sentence-transformers model name, or "hash" for an offline,
# dependency-free fallback (fine for tests, weaker for real retrieval)
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def driver():
    """A Neo4j driver for the configured database (Chapter 4)."""
    from neo4j import GraphDatabase
    # Server notifications (e.g. GDS deprecation notices on procedure fields)
    # are harmless here and would clutter the lab output.
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD),
                                notifications_min_severity="OFF")
