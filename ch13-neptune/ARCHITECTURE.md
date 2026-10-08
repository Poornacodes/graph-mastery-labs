# Listings 13.3 and 13.4 (conceptual)

## Listing 13.3 — Data-lake pipelines feeding Neptune

```text
Batch:
  Sources -> S3 (raw) -> AWS Glue (transform to Neptune CSV/RDF)
          -> S3 (curated) -> Neptune Bulk Loader -> Neptune Database
          -> snapshot/load -> Neptune Analytics (analysis / GraphRAG)
  Orchestrated by Step Functions / MWAA / EventBridge schedule

Streaming:
  Change events (Kinesis / MSK / DynamoDB Streams)
          -> AWS Lambda (map event -> openCypher/Gremlin upsert)
          -> Neptune Database   (MERGE-style, idempotent)
```

`bulk-load/` holds a minimal pair of files in the Neptune Gremlin CSV format
the Bulk Loader expects (`~id`, `~label`, typed property columns).

## Listing 13.4 — Reference architecture for native-AWS GraphRAG

```text
   Documents in S3 (data lake)
        │  ingest
   Amazon Bedrock Knowledge Base (GraphRAG)
        ├─ embeddings (a Bedrock embedding model)
        └─ entity + relationship graph
              stored in  ▼
        Amazon Neptune Analytics  (graph + vector store)
        │  RetrieveAndGenerate (hybrid retrieval)
   Amazon Bedrock foundation model  → grounded, cited answer
        │
   Your app  (Lambda / API Gateway / Bedrock Agent)
```

## The local lab, mapped to AWS (Try It Yourself 13.1, no-cost path)

| In this repository | On AWS |
|---|---|
| sentence-transformers embeddings (`graphlab/embed.py`) | A Bedrock embedding model |
| Neo4j with a vector index (`ch09-graphrag`, `examples/athena`) | Neptune Analytics (graph + vector store) |
| `graphlab/llm.py` generation (Ollama / Anthropic) | A Bedrock foundation model (`LLM_PROVIDER=bedrock`) |
| FastAPI service (`ch08-fullstack-app`, `examples/athena/api.py`) | Lambda behind API Gateway, or a Bedrock Agent |
| Neo4j / JanusGraph / Fuseki | Neptune Database (openCypher, Gremlin, SPARQL) |
| `ch07-modeling-etl` loader | Glue + the Neptune Bulk Loader from S3 |
