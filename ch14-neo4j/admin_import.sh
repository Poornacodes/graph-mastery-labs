#!/usr/bin/env bash
# Listing 14.3. Try It Yourself 14.1, part 3 — build a database offline with neo4j-admin
# import, into a throwaway volume (your lab database is not touched), then
# start it on ports 17474/17687, count what arrived, and clean up.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
IMAGE=neo4j:5-community
"$PY" gen_import_csv.py --people "${PEOPLE:-1000000}" --follows "${FOLLOWS:-5000000}"

docker volume rm gm14_import >/dev/null 2>&1 || true
start=$(date +%s)
docker run --rm -v gm14_import:/data -v "$PWD/import-demo:/import" "$IMAGE" \
  neo4j-admin database import full \
    --nodes=/import/persons.csv --relationships=/import/follows.csv \
    --overwrite-destination=true neo4j | tail -4
echo "import took $(( $(date +%s) - start )) s"

docker run -d --name gm14-imported -p 17474:7474 -p 17687:7687 \
  -e NEO4J_AUTH=neo4j/graphmastery -v gm14_import:/data "$IMAGE" >/dev/null
for _ in $(seq 1 60); do
  docker exec gm14-imported cypher-shell -u neo4j -p graphmastery "RETURN 1" \
    >/dev/null 2>&1 && break
  sleep 2
done
docker exec gm14-imported cypher-shell -u neo4j -p graphmastery \
  "MATCH (p:Person) WITH count(p) AS people
   MATCH ()-[f:FOLLOWS]->() RETURN people, count(f) AS follows"

if [ "${KEEP:-0}" != 1 ]; then
  docker rm -f gm14-imported >/dev/null && docker volume rm gm14_import >/dev/null
  echo "cleaned up (set KEEP=1 to keep the imported database running)"
fi
