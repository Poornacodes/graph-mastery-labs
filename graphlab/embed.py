"""Sentence embeddings for GraphRAG (Chapter 9).

Uses sentence-transformers (all-MiniLM-L6-v2, 384 dimensions, runs on a
laptop CPU). Set EMBED_MODEL=hash for an offline fallback that needs no
model download: a hashed bag of words, good enough for the smoke test but
much weaker than a real embedding model.
"""
from __future__ import annotations

import hashlib
import math
import re

from . import config

HASH_DIM = 384
_model = None


def dimensions() -> int:
    if config.EMBED_MODEL == "hash":
        return HASH_DIM
    return _st().get_sentence_embedding_dimension()


def embed(texts: list[str] | str) -> list[list[float]] | list[float]:
    single = isinstance(texts, str)
    batch = [texts] if single else list(texts)
    if config.EMBED_MODEL == "hash":
        vecs = [_hash_embed(t) for t in batch]
    else:
        vecs = _st().encode(batch, normalize_embeddings=True).tolist()
    return vecs[0] if single else vecs


def _st():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(config.EMBED_MODEL)
    return _model


def _hash_embed(text: str) -> list[float]:
    vec = [0.0] * HASH_DIM
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        h = int(hashlib.md5(word.encode()).hexdigest(), 16)
        vec[h % HASH_DIM] += 1.0 if (h >> 8) % 2 else -1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]
