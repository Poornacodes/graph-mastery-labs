#!/usr/bin/env bash
# Listing 14.4. Try It Yourself 14.1, part 4 — an offline backup and a verified restore.
# Community Edition dumps a stopped database: stop the lab Neo4j, dump its
# volume, start it again; then load the dump into a THROWAWAY volume and
# count its nodes, proving the backup restores. Your lab data is not changed.
set -euo pipefail
cd "$(dirname "$0")"
IMAGE=neo4j:5-community
VOLUME=graph-mastery-labs_neo4j_data
mkdir -p backups

docker compose -f ../docker-compose.yml stop neo4j
start=$(date +%s)
docker run --rm -v "$VOLUME:/data" -v "$PWD/backups:/backups" "$IMAGE" \
  neo4j-admin database dump neo4j --to-path=/backups --overwrite-destination=true
echo "dump took $(( $(date +%s) - start )) s; file:"; ls -lh backups/neo4j.dump
docker compose -f ../docker-compose.yml start neo4j

docker volume rm gm14_restore >/dev/null 2>&1 || true
docker run --rm -v gm14_restore:/data -v "$PWD/backups:/backups" "$IMAGE" \
  neo4j-admin database load neo4j --from-path=/backups --overwrite-destination=true
docker run -d --name gm14-restored -p 27474:7474 -p 27687:7687 \
  -e NEO4J_AUTH=neo4j/graphmastery -v gm14_restore:/data "$IMAGE" >/dev/null
for _ in $(seq 1 60); do
  docker exec gm14-restored cypher-shell -u neo4j -p graphmastery "RETURN 1" \
    >/dev/null 2>&1 && break
  sleep 2
done
echo "restored copy:"
docker exec gm14-restored cypher-shell -u neo4j -p graphmastery \
  "MATCH (n) RETURN count(n) AS nodes"
docker rm -f gm14-restored >/dev/null && docker volume rm gm14_restore >/dev/null
echo "restore verified and cleaned up; the dump stays in ch14-neo4j/backups/"
