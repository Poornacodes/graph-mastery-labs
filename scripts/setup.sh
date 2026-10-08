#!/usr/bin/env bash
# One-command setup (Appendix A): Python environment, lab databases, smoke test.
#   ./scripts/setup.sh            # core labs
#   ./scripts/setup.sh --gremlin  # also start JanusGraph for the Gremlin labs
set -euo pipefail
cd "$(dirname "$0")/.."

command -v docker >/dev/null || { echo "Install Docker Desktop first."; exit 1; }
docker info >/dev/null 2>&1 || { echo "Start Docker Desktop, then rerun."; exit 1; }
PY="${PYTHON:-python3}"
"$PY" -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ needed"'

[ -f .env ] || cp .env.example .env
[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/pip install --upgrade pip >/dev/null
.venv/bin/pip install -r requirements.txt

if [ "${1:-}" = "--gremlin" ]; then
  docker compose --profile gremlin up -d
else
  docker compose up -d
fi

echo "Waiting for Neo4j (the first start downloads the APOC and GDS plugins)..."
for _ in $(seq 1 60); do
  [ "$(docker inspect -f '{{.State.Health.Status}}' gm-neo4j 2>/dev/null)" = healthy ] && break
  sleep 5
done

.venv/bin/python scripts/smoke_test.py --quick
echo
echo "Ready. Activate the environment with:  source .venv/bin/activate"
echo "Neo4j Browser: http://localhost:7474  (neo4j / graphmastery)"
