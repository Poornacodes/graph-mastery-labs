"""Listing 5.2 against a Gremlin Server (the optional JanusGraph container:
`docker compose --profile gremlin up -d`)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from graphlab import config


def run_5_2():
    from gremlin_python.driver.client import Client
    client = Client(config.GREMLIN_URL, "g")
    try:
        client.submit("g.V().has('Person','name',within('Alice','Bob','Carol',"
                      "'Dave')).drop()").all().result()
        client.submit((Path(__file__).with_name("knows.groovy")).read_text()
                      .split("\n", 1)[1]).all().result()
        direct = client.submit("g.V().has('Person','name','Alice')."
                               "out('knows').values('name')").all().result()
        fof = client.submit("g.V().has('Person','name','Alice').out('knows')."
                            "out('knows').dedup().values('name')").all().result()
        return {"direct": sorted(direct), "friend-of-friend": sorted(fof)}
    finally:
        client.close()


if __name__ == "__main__":
    for k, v in run_5_2().items():
        print(f"Gremlin {k:<17}", v)
