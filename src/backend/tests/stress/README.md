# Telemetry write stress test

`stress_telemetry_writes.py` is a manual harness for reproducing the
"transactions + vertex_builds eat the DB pool" failure mode and verifying
fixes against it.

It bypasses the FastAPI / locust / flow-execution layer and hammers
`transaction_service.log_transaction()` and `flowos_core.graph.utils.log_vertex_build()`
directly from many concurrent coroutines, which mirrors what the per-vertex
`BackgroundTasks` workers do during heavy flow load (but without needing an
OpenAI key or a real flow to run).

## Run against SQLite

```bash
uv run python src/backend/tests/stress/stress_telemetry_writes.py \
    --concurrency 200 --seconds 15
```

## Run against Postgres

```bash
# Start a throwaway Postgres
docker run --rm -d --name flowos-pg-test -p 55432:5432 \
    -e POSTGRES_PASSWORD=flowos -e POSTGRES_USER=flowos \
    -e POSTGRES_DB=flowos postgres:16

export DB_URL="postgresql+psycopg://flowos:flowos@localhost:55432/flowos"  # pragma: allowlist secret
# (or any standard postgres DSN, e.g. "$FLOWOS_DATABASE_URL" if set)
uv run python src/backend/tests/stress/stress_telemetry_writes.py \
    --concurrency 200 --seconds 15
```

## Toggle the writer off to reproduce the legacy failure mode

```bash
FLOWOS_TELEMETRY_WRITER_ENABLED=false \
FLOWOS_DB_CONNECTION_SETTINGS='{"pool_size":5,"max_overflow":5,"pool_timeout":3}' \
    uv run python src/backend/tests/stress/stress_telemetry_writes.py \
        --concurrency 500 --seconds 15
```

## What to look for
- `error_total=0` — neither SQLite "database is locked" nor Postgres
  pool-timeout exceptions should fire when the writer is enabled.
- `enq_tx` / `enq_vb` counters match producer success counts.
- After a sufficient drain grace, the DB row counts should match the
  enqueued counts (modulo retention).
