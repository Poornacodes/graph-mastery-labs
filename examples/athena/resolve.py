"""Section E.4 — Entity resolution.

Clusters obvious duplicates with graphlab/resolve.py's rules ("R. Okafor",
"Okafor" -> "Rina Okafor"), then folds each alias into its canonical node
with Listing E.3. It also embeds the remaining names and prints near-duplicate
pairs the rules did not merge, as a queue for human review.
"""
from common import ROOT  # noqa: F401  (sets the import path)
from graphlab import config, embed, neo
from graphlab.resolve import clusters

# Listing E.3 — Merging resolved duplicates
# (mergeRels: true also folds the alias's now-duplicate edges into one)
MERGE_ALIASES = """
MATCH (canonical:Entity {name: $canonical})
MATCH (alias:Entity) WHERE alias.name IN $aliases
CALL apoc.refactor.mergeNodes([canonical, alias],
                              {properties: 'discard', mergeRels: true})
YIELD node RETURN node.name AS name
"""


def review_queue(names_by_type, threshold=0.85):
    if config.EMBED_MODEL == "hash":
        return []
    names = sorted(names_by_type)
    vecs = dict(zip(names, embed.embed(names)))
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if names_by_type[a] == names_by_type[b]:
                sim = sum(x * y for x, y in zip(vecs[a], vecs[b]))
                if sim >= threshold:
                    pairs.append((round(sim, 2), a, b))
    return sorted(pairs, reverse=True)


def main():
    rows = neo.run("MATCH (e:Entity) RETURN e.name AS name, e.type AS type")
    names_by_type = {r["name"]: r["type"] for r in rows}
    canonical = clusters(names_by_type)
    groups = {}
    for alias, canon in canonical.items():
        if alias != canon:
            groups.setdefault(canon, []).append(alias)
    for canon, aliases in sorted(groups.items()):
        neo.run(MERGE_ALIASES, canonical=canon, aliases=aliases)
        print(f"  = merged {aliases} -> {canon!r}")
    after = neo.run("MATCH (e:Entity) RETURN count(e) AS n")[0]["n"]
    print(f"Entities: {len(rows)} -> {after}")
    remaining = {r["name"]: r["type"] for r in
                 neo.run("MATCH (e:Entity) RETURN e.name AS name, e.type AS type")}
    queue = review_queue(remaining)
    if queue:
        print("Similar names left unmerged (review by hand):")
        for sim, a, b in queue:
            print(f"  ? {sim}  {a!r} / {b!r}")


if __name__ == "__main__":
    main()
