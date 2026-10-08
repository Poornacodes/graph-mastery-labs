# Try It Yourself 12.1 — containerize the recommender

The `api/` folder holds a copy of the Chapter 8 app (`ch08-fullstack-app/app.py`
and its page). The smoke test checks the copy still matches the original.

## 1. Start the stack (Listing 12.1)

```bash
# from the repository root: free the ports used by the lab stack
docker compose down
cd ch12-production
cp .env.example .env
docker compose up -d --build
docker compose ps          # neo4j "healthy", api "running"
```

## 2. Load data into the new database

The stack has its own, empty database volume. Load the Chapter 7 dataset into
it (from the host, the database is still on localhost:7687):

```bash
cd ../ch07-modeling-etl
python generate_ratings.py
python listing_7_1_loader.py
```

## 3. Confirm the API reaches the database by service name

```bash
curl http://localhost:8000/users/1/recommendations
docker compose exec api env | grep NEO4J_URI     # bolt://neo4j:7687
```

Inside the `api` container, `localhost` is the container itself, so the API
must reach Neo4j by its service name, `neo4j`. Change `NEO4J_URI` to
`bolt://localhost:7687` in `docker-compose.yml`, run `docker compose up -d`,
and watch the API fail; then change it back.

## 4. (Optional) Neo4j Aura Free

Create a free instance at console.neo4j.io (no card needed), load the data
with `NEO4J_URI=neo4j+s://<id>.databases.neo4j.io NEO4J_PASSWORD=<generated>
python listing_7_1_loader.py`, and run the API against it the same way. Only
the connection settings change; the driver code is identical. `neo4j+s://`
means an encrypted (TLS) connection with routing.

## 5. Journal: your operating targets

| Question | Your answer |
|---|---|
| RPO: how much data can you afford to lose? | |
| RTO: how fast must you be back? | |
| Backup method and schedule that meets the RPO | |
| How and how often you test a restore | |
| Alert 1 (e.g. p99 query latency over 500 ms for 5 minutes) | |
| Alert 2 (e.g. error rate over 1% on the API) | |
| Alert 3 (e.g. heap or page-cache pressure, disk over 80%) | |

## 6. Clean up

```bash
docker compose down        # add -v to delete the database volume too
cd .. && docker compose up -d   # bring the lab stack back
```
