"""Rule-based entity resolution for obvious duplicates (Section 11.4).

Two names of the same type are the same entity when one name's words all
appear in the other ("Okafor" ~ "Rina Okafor", "Orion" ~ "Project Orion"),
or when they differ only by initials ("R. Okafor" ~ "Rina Okafor"). A title
such as "Dr." is ignored. The longest name in a cluster becomes canonical.
"""
from __future__ import annotations

import re

TITLES = {"dr", "mr", "mrs", "ms", "prof", "inc", "ltd"}


def tokens(name: str) -> list[str]:
    return [t for t in re.sub(r"[^a-z0-9 ]", " ", name.lower()).split()
            if t not in TITLES]


def same_entity(a: str, b: str) -> bool:
    short, long_ = sorted([tokens(a), tokens(b)], key=len)
    if not short:
        return False
    if all(t in long_ for t in short):
        return True
    # Same length, same last word, other words equal or an initial of each
    # other ("r" ~ "rina"). Whole words must match exactly: "platform" and
    # "perception" share a first letter but are different teams.
    if len(short) != len(long_) or short[-1] != long_[-1]:
        return False
    return all(x == y or (min(len(x), len(y)) == 1 and x[0] == y[0])
               for x, y in zip(short[:-1], long_[:-1]))


def clusters(names_by_type: dict[str, str]) -> dict[str, str]:
    """Map every name to its canonical name (itself if it has no duplicate)."""
    canonical: dict[str, str] = {}
    for name in sorted(names_by_type, key=lambda n: (-len(n), n)):
        match = next((c for c in dict.fromkeys(canonical.values())
                      if names_by_type[c] == names_by_type[name]
                      and same_entity(name, c)), None)
        canonical[name] = match or name
    return canonical
