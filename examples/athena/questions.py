"""Section E.6 — the four competency questions (Listing E.4), then the GDS
analytics Athena surfaces beside its answers: PageRank for the most central
people and components, Louvain for team clusters."""
from common import HERE
from graphlab import neo

PARAMS = {"person": "Tomas Lind", "team": "Platform Team",
          "product": "Helios Picker", "departed": "Elena Vance"}
TITLES = ["Q1 Who leads the project Tomas Lind works on?",
          "Q2 Which projects depend on a component the Platform Team builds?",
          "Q3 What has Helios announced about the Helios Picker, and who worked on it?",
          "Q4 Who is within two steps of Elena Vance, who left Project Orion?"]


def main():
    for title, rows in zip(TITLES, neo.run_file(HERE / "questions.cypher", **PARAMS)):
        print(title)
        for r in rows:
            print("   ", r)

    neo.run("CALL gds.graph.exists('athena') YIELD exists WITH exists "
            "WHERE exists CALL gds.graph.drop('athena') YIELD graphName "
            "RETURN graphName")
    neo.run("CALL gds.graph.project('athena', 'Entity', "
            "{REL: {orientation: 'UNDIRECTED'}})")
    print("\nMost central (PageRank):")
    for r in neo.run("""CALL gds.pageRank.stream('athena') YIELD nodeId, score
                        WITH gds.util.asNode(nodeId) AS e, score
                        WHERE e.type IN ['Person', 'Component']
                        RETURN e.name AS name, e.type AS type,
                               round(score, 3) AS pagerank
                        ORDER BY pagerank DESC LIMIT 5"""):
        print("   ", r)
    print("Clusters (Louvain):")
    for r in neo.run("""CALL gds.louvain.stream('athena')
                        YIELD nodeId, communityId
                        WITH communityId, collect(gds.util.asNode(nodeId).name) AS members
                        WHERE size(members) > 2
                        RETURN communityId, members ORDER BY size(members) DESC"""):
        print("   ", r["members"])
    neo.run("CALL gds.graph.drop('athena')")


if __name__ == "__main__":
    main()
