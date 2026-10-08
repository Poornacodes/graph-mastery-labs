"""Shared setup for the Athena scripts: import path, chunk reader."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))


def load_chunks(path="examples/athena/corpus/"):
    """Yield (chunk_id, text): one chunk per paragraph of each document.
    Relative paths resolve from the repository root, as in Listing E.2."""
    folder = Path(path) if Path(path).is_absolute() else ROOT / path
    for doc in sorted(folder.glob("*.txt")):
        paragraphs = [p.strip() for p in doc.read_text().split("\n\n")]
        for i, para in enumerate(p for p in paragraphs if p):
            yield f"{doc.name}#{i}", para
