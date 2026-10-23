#!/usr/bin/env bash
# Listing 14.1. Try It Yourself 14.1, part 1 — ask Neo4j how to size its memory for a
# machine with the given RAM (default 8g), based on your actual store size.
docker exec gm-neo4j neo4j-admin server memory-recommendation --memory="${1:-8g}"
echo
echo "Current settings in the container:"
docker exec gm-neo4j sh -c 'grep -E "^server\.memory" /var/lib/neo4j/conf/neo4j.conf'
