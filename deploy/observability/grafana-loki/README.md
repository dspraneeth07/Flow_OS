# FlowOS on Grafana + Loki

Reference stack that ingests FlowOS's structured JSON logs into [Loki](https://grafana.com/oss/loki/) and visualizes them with a pre-provisioned Grafana dashboard.

Use this as a starting point. The compose file, Promtail config, and dashboard JSON are independent of the rest of `deploy/` and can be lifted into any environment.

## What you get

- **Loki 3.2** on `:3100`
- **Promtail 3.2** scraping a directory of FlowOS log files
- **Grafana 11.3** on `:3000` with the Loki datasource and the `FlowOS Logs` dashboard already provisioned

## Prerequisites on the FlowOS side

The dashboard expects FlowOS to be running in JSON mode with service metadata set. At minimum:

```bash
FLOWOS_LOG_ENV=container
FLOWOS_LOG_FILE=/absolute/path/to/flowos/logs/flowos.log
FLOWOS_SERVICE_NAME=flowos
FLOWOS_VERSION=1.10.0
FLOWOS_ENVIRONMENT=production
```

Promtail scrapes a directory of `*.log` files, so `FLOWOS_LOG_FILE` must point at a file inside
the directory you expose to Promtail as `FLOWOS_LOG_DIR` (see [Run](#run)). Set both to the same
directory, otherwise Promtail watches an empty folder and the dashboard stays blank. Use an
absolute path: `FLOWOS_LOG_FILE` is resolved against FlowOS's working directory, not this one.

In JSON mode the file is a single JSON stream: application logs and third-party stdlib loggers
(`uvicorn`, `sqlalchemy`, `httpx`, `langchain`) are all rendered as JSON and run through PII
redaction, so the `json` parse stage and the **Stdlib intercept routing** panel work against it
directly. This stack scrapes a file, so `FLOWOS_LOG_FILE` is required. If you instead run
FlowOS as a container, you can drop the file and scrape its stdout by swapping Promtail's
`static_configs` file target for `docker_sd_configs` (same JSON, same labels).

See [Logs and observability](../../../docs/docs/Develop/observability-grafana-loki.mdx) for the full list of environment variables (per-logger overrides, extra PII redaction keys, trace correlation, etc.).

## Run

From this directory:

```bash
# Point Promtail at the directory that holds the file you set in
# FLOWOS_LOG_FILE above. Must be the same directory. Defaults to the
# bundled ./logs (used by the quick smoke test below).
export FLOWOS_LOG_DIR=/absolute/path/to/flowos/logs

docker compose up -d
```

Then open [http://localhost:3000/d/flowos-prod-logs](http://localhost:3000/d/flowos-prod-logs). Default credentials are `admin` / `admin` (override with `GF_ADMIN_USER` and `GF_ADMIN_PASSWORD`).

To stop:

```bash
docker compose down -v
```

### Quick smoke test (no FlowOS required)

To verify the stack end to end without running FlowOS, write a sample record into the bundled
`./logs` directory and query Loki directly:

```bash
mkdir -p logs
echo '{"event":"smoke test","level":"info","logger":"flowos.api.run","timestamp":"2026-06-01T00:00:00Z","service":"flowos","environment":"production","version":"1.10.0"}' >> logs/flowos.log

docker compose up -d

# Give Promtail a few seconds to tail the file, then confirm the line reached Loki:
sleep 5
curl -sG 'http://localhost:3100/loki/api/v1/query_range' --data-urlencode 'query={job="flowos"}' | grep -q "smoke test" && echo "OK: log reached Loki"
```

## What each dashboard panel proves

| Panel | LogQL it runs |
|---|---|
| **PII leak count (must be 0)** | `sum(count_over_time({job="flowos"} \|~ "sk-do-not-leak\|hunter2\|Bearer xyz" [$__range]))` |
| **Errors with structured tracebacks** | `{job="flowos", level=~"error\|critical"} \|= "exception" \| json` |
| **Redaction proof** | `{job="flowos"} \|~ "\\*\\*\\*"` |
| **Stdlib intercept routing** | `{job="flowos", logger=~"uvicorn.*\|sqlalchemy.*\|httpx.*\|langchain.*"}` |
| **Service / environment / version coverage** | `sum by (service, environment, version) (count_over_time({job="flowos"}[$__range]))` |
| **Log rate by level** | `sum by (level) (rate({job="flowos"}[1m]))` |
| **Log rate by logger** | `topk(10, sum by (logger) (rate({job="flowos"}[1m])))` |

## Notes

- Promtail only promotes `level`, `service`, `environment`, `version`, `logger` to labels. High-cardinality fields (`user_id`, `flow_id`, `trace_id`) stay in the log body — query them with `| json` in LogQL.
- Replace Promtail with [Grafana Alloy](https://grafana.com/oss/alloy/) if you already standardize on it; the JSON parse stage maps 1:1.
- If your runtime ships logs through a different transport (Fluent Bit, Vector, OTLP), only the scrape side changes — the dashboard and label schema stay the same.
