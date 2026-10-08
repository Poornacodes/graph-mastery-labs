# Athena's API image (Section E.10). Build from the repository root:
#   docker compose -f examples/athena/docker-compose.yml up -d --build
FROM python:3.12-slim
WORKDIR /repo
RUN pip install --no-cache-dir fastapi uvicorn neo4j sentence-transformers anthropic
COPY graphlab/ graphlab/
COPY examples/athena/ examples/athena/
WORKDIR /repo/examples/athena
EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
