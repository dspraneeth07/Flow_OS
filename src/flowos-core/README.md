# FLOWOS_CORE - FlowOS Executor

The FlowOS Executor (FLOWOS_CORE) is a command-line tool that serves and runs flows statelessly from flow JSON files with minimal dependencies.

Running a flow with FLOWOS_CORE is similar to running flows with the `--backend-only` environment variable enabled, but even more lightweight because the FlowOS package and all of its dependencies don't need to be installed.

FLOWOS_CORE uses a no-op database interface called [`NoopSession`](https://github.com/flowos-ai/flowos/blob/main/src/flowos-core/src/flowos_core/services/session.py) for all operations that require persistent state.
There is no `flowos.db` database file when using FLOWOS_CORE.
You can run flows with the API, but any stateful operations that depend on the FlowOS database, like saving flows, storing messages, or managing users **will not** persist data.
Operations that depend on `flowos.db` will not work as they do in the full FlowOS application.

Memory operations are dispatched at call time, not at import time.
If the `flowos` package is installed in the same Python environment as `flowos_core` and a real database service is registered, memory operations are routed to the full `flowos.memory` implementation instead. This applies when `flowos_core` is used as a Python library inside a running FlowOS server, not when running `flowos_core run` or `flowos_core serve` from the command line.

## Commands

**Runtime commands** — documented in this README:

| Command | Description |
|---------|-------------|
| [`flowos_core serve`](#serve-the-simple-agent-starter-flow-with-flowos_core-serve) | Serve one or more flows as FastAPI endpoints at `/flows/{flow_id}/run` |
| [`flowos_core run`](#run-the-simple-agent-flow-with-flowos_core-run) | Execute a flow locally and stream results to `stdout` |
| [`flowos-mcp`](#flowos-mcp) | Start an MCP server that connects to a running FlowOS instance |

**Flow DevOps SDK commands** — documented in the [Flow DevOps Toolkit](https://docs.flowos.org/flow-devops-sdk):

| Command | Description |
|---------|-------------|
| `flowos_core init` | Scaffold a versioned flow project with CI templates |
| `flowos_core login` | Validate credentials against a remote FlowOS instance |
| `flowos_core create` | Create a new flow JSON from a built-in or custom template |
| `flowos_core validate` | Validate flow JSON before pushing |
| `flowos_core requirements` | Generate `requirements.txt` from a flow's component dependencies |
| `flowos_core status` | Compare local flow files against a remote FlowOS instance |
| `flowos_core push` | Push flows to a remote instance by stable ID |
| `flowos_core pull` | Pull flows from a remote instance to local files |
| `flowos_core export` | Normalize flow JSON for clean git diffs |

## Prerequisites

- Install [Python](https://www.python.org/downloads/release/python-3100/).
- Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
- Create or download a flow JSON file. For example, download the Simple Agent flow from the repository:

  ```bash
  curl -o simple-agent-flow.json "https://raw.githubusercontent.com/flowos-ai/flowos/main/src/backend/base/flowos/initial_setup/starter_projects/Simple%20Agent.json"
  ```

- Create an [OpenAI API key](https://platform.openai.com/api-keys).
- Create a FlowOS API key. For FLOWOS_CORE, you can generate a secure token locally (see [Serve the simple agent starter flow with `flowos_core serve`](#serve-the-simple-agent-starter-flow-with-flowos_core-serve)), or create one through the FlowOS server UI or CLI.

## Install FLOWOS_CORE

FLOWOS_CORE can be installed in multiple ways. If you have installed FlowOS OSS version >=1.6, `flowos_core` is already included.

### Clone repository

1. Clone the FlowOS repository:

   ```bash
   git clone https://github.com/flowos-ai/flowos
   ```

2. Change directory to `flowos/src/flowos-core`:

   ```bash
   cd flowos/src/flowos-core
   ```

   From this directory, you can run `flowos_core` commands using `uv run flowos_core` as shown in [flowos_core serve](#serve-the-simple-agent-starter-flow-with-flowos_core-serve) or [flowos_core run](#run-the-simple-agent-flow-with-flowos_core-run).

### Install from PyPI

1. Create and activate a virtual environment:

   ```bash
   uv venv flowos_core-venv
   source flowos_core-venv/bin/activate
   ```

2. Install the FLOWOS_CORE package from PyPI:

   ```bash
   uv pip install flowos_core
   ```

   To install the latest nightly (pre-release) version of FLOWOS_CORE:

   ```bash
   uv pip install --pre flowos_core
   ```

   To run `flowos_core` commands, continue to [flowos_core serve](#serve-the-simple-agent-starter-flow-with-flowos_core-serve) or [flowos_core run](#run-the-simple-agent-flow-with-flowos_core-run).

### Run without installing

Run FLOWOS_CORE without installing it locally using `uvx`.

1. Create a FlowOS API key (see [Serve](#serve-the-simple-agent-starter-flow-with-flowos_core-serve)), and set `FLOWOS_API_KEY` in the same terminal session as `flowos_core`:

   ```bash
   export FLOWOS_API_KEY="sk..."
   ```

2. Run `flowos_core serve` using `uvx`:

   ```bash
   uvx flowos_core serve simple-agent-flow.json
   ```

   This command downloads and runs FLOWOS_CORE in a temporary environment without permanent installation. From the same environment, you can also run flows directly with [flowos_core run](#run-the-simple-agent-flow-with-flowos_core-run).

## Serve the simple agent starter flow with `flowos_core serve`

`flowos_core serve` starts a FastAPI server that hosts one or more flows. You can load flows at startup from files or a directory, or start with an empty registry and upload flows via the API. Once running, flows are available at `POST /flows/{flow_id}/run`.

`flowos_core serve` accepts a `.json` flow file or a `.py` Python script (same as `flowos_core run`), as well as inline JSON via `--flow-json` or piped input via `--stdin`.

`flowos_core serve` accepts a `.json` flow file or a `.py` Python script (same as `flowos_core run`), as well as inline JSON via `--flow-json` or piped input via `--stdin`.

The API key is required for security because `flowos_core serve` can create a publicly accessible FastAPI server.

This example uses the **Agent** component's built-in OpenAI model, which requires an OpenAI API key. If you want to use a different provider, edit the model provider, model name, and credentials accordingly.

1. Generate a FlowOS API key.

   For FLOWOS_CORE, you can generate a secure token locally to use as your `FLOWOS_API_KEY`:

   ```bash
   uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   This is different from creating a FlowOS API key through the FlowOS server UI or CLI, which stores the key in the FlowOS database. For FLOWOS_CORE, you only need a secure token string to authenticate requests to your FLOWOS_CORE server.

2. Set up your environment variables using one of the following options.

   **Option: .env file**

   Create a `.env` file and populate it with your flow's variables. The `FLOWOS_API_KEY` is required. This example assumes the flow requires an OpenAI API key.

   ```bash
   FLOWOS_API_KEY="sk..."
   OPENAI_API_KEY="sk-..."
   ```

   **Option: Export variables**

   Export your variables in the same terminal session where you'll start the server. You must declare your variables before the server starts for the server to pick them up.

   ```bash
   export FLOWOS_API_KEY="sk..."
   export OPENAI_API_KEY="sk-..."
   ```

3. Install dependencies.

   If you already have FlowOS installed, or if you're running from source at `src/flowos-core`, FLOWOS_CORE is included with FlowOS and all dependencies are already available. You don't need to install additional dependencies.

   If you install the standalone `flowos_core` package from [PyPI](https://pypi.org/project/flowos_core/) or run FLOWOS_CORE with `uvx`, you need to manually install the dependencies required by the components in your flow.

   To find which dependencies your flow requires:

   1. Run your flow with [flowos_core run](#run-the-simple-agent-flow-with-flowos_core-run):

      ```bash
      uv run flowos_core run simple-agent-flow.json "test input"
      ```

      FLOWOS_CORE reports any missing dependencies in the subsequent error message.
   2. Install the missing dependencies that FLOWOS_CORE reports.

   For example, to run the simple agent template flow, install these dependencies in your environment before running the simple agent flow:

   ```bash
   uv pip install "langchain~=0.3.23" "langchain-core<1.0.0" "langchain-community" "langchain-openai" "langchain-text-splitters" beautifulsoup4 lxml requests
   ```

4. Start the server with your variable values using one of the following options.

   **Option: .env file**

   This example assumes your flow file and `.env` file are in the current directory:

   ```bash
   uv run flowos_core serve simple-agent-flow.json --env-file .env
   ```

   If your `.env` file is in a different location, provide the full or relative path:

   ```bash
   uv run flowos_core serve simple-agent-flow.json --env-file /path/to/.env
   ```

   **Option: Export variables**

   If you exported your variables, the command to start the server automatically picks up the values when it starts:

   ```bash
   uv run flowos_core serve simple-agent-flow.json
   ```

   To export new values, stop the server, export the variables, and then start the server again.

5. The startup process displays a `flow_id` value in the output. Copy the `flow_id` to use in the test API call in the next step. In this example, the `flow_id` is `c1dab29d-3364-58ef-8fef-99311d32ee42`:

   ```
    FLOWOS_CORE Server
    Flow loaded: simple-agent-flow.json (c1dab29d-3364-58ef-8fef-99311d32ee42)
    Server:      http://127.0.0.1:8000
    Run flows at: POST /flows/{flow_id}/run
    API key:     x-api-key header or ?x-api-key= query parameter
   ```

6. To send a test request to the server, open a new terminal and export your `flow_id` and FlowOS API key values as variables:

   ```bash
   export FLOWOS_API_KEY="sk..."
   export FLOW_ID="c1dab29d-3364-58ef-8fef-99311d32ee42"
   ```

7. Test the server with an API call to the `/flows/flow_id/run` endpoint:

   ```bash
   curl -X POST http://localhost:8000/flows/$FLOW_ID/run \
     -H "Content-Type: application/json" \
     -H "x-api-key: $FLOWOS_API_KEY" \
     -d '{"input_value": "Hello, world!"}'
   ```

   Successful response example:

   ```json
   {
     "result": "Hello world! 👋\n\nHow can I help you today? If you have any questions or need assistance, just let me know!",
     "success": true,
     "logs": "\n\n\u001b[1m> Entering new None chain...\u001b[0m\n\u001b[32;1m\u001b[1;3mHello world! 👋\n\nHow can I help you today?...\u001b[0m\n\n\u001b[1m> Finished chain.\u001b[0m\n",
     "type": "message",
     "component": "Chat Output"
   }
   ```

Your flow is now running as a lightweight API endpoint, with only the flow's required dependencies and no visual builder installed. Users who call your endpoint don't need to install FlowOS or configure their own LLM provider keys.

To make your server publicly accessible, use a tunneling service like ngrok or deploy to a public cloud provider.

### HTTP endpoints

The FLOWOS_CORE server exposes the following endpoints. All `/flows/{flow_id}` routes require the `x-api-key` header or `?x-api-key=` query parameter.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/flows` | GET | List all served flows and their metadata |
| `/flows/upload/` | POST | Upload a flow JSON to the registry (accepts full FlowOS export format) |
| `/flows/{flow_id}/run` | POST | Run the flow and return a single response |
| `/flows/{flow_id}/stream` | POST | Run the flow and stream output as server-sent events |
| `/flows/{flow_id}/info` | GET | Return flow metadata (title, description, input/output types) |
| `/health` | GET | Global health check — returns `{"status": "ok"}` |
| `/docs` | GET | Auto-generated OpenAPI/Swagger UI |

### Request body schema

**`POST /flows/{flow_id}/run`**

```json
{
  "input_value": "Your message here",
  "session_id": "optional-conversation-id"
}
```

`session_id` is optional. When set, Agent and Memory components use it to maintain conversation history across multiple calls. If omitted, a new session ID is generated for each request.

**`POST /flows/{flow_id}/stream`**

```json
{
  "input_value": "Your message here",
  "input_type": "chat",
  "output_type": "chat",
  "output_component": null,
  "session_id": "optional-conversation-id",
  "tweaks": {"ComponentName": {"param": "value"}}
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `input_value` | — | Required. Input passed to the flow. |
| `input_type` | `"chat"` | Input type: `chat` or `text`. |
| `output_type` | `"chat"` | Output type: `chat`, `text`, `debug`, or `any`. |
| `output_component` | `null` | Pin output to a specific component by name. |
| `session_id` | `null` | Conversation ID for memory continuity across requests. |
| `tweaks` | `null` | Per-request parameter overrides. Keys are component names; values are dicts of parameter overrides. Use this to parameterize a flow without modifying the JSON. |

### Response schema

The FLOWOS_CORE server's response schema is different from the FlowOS API `/run` endpoint's schema. Requests to the FLOWOS_CORE server's `/flows/{flow_id}/run` endpoint return the following fields:

```json
{
  "result": "string",      // Output result from the flow execution
  "success": true,         // Whether execution was successful
  "logs": "string",        // Captured logs from execution
  "type": "message",       // Type of result
  "component": "string"    // The component that generated the result (e.g. "Chat Output")
}
```

The `/stream` endpoint returns the same fields as server-sent events, with one event per component output.

### Serve multiple flows at startup

You can pass a directory, multiple file paths, or a mix of both to load several flows at startup. Each flow is registered under its own ID.

```bash
# Serve every .json file in a directory (top-level only, not recursive)
uv run flowos_core serve flows/

# Serve specific files
uv run flowos_core serve flow-a.json flow-b.json

# Mix directory and individual files
uv run flowos_core serve flows/ extra-flow.json
```

Python `.py` script flows are also supported when using a single worker:

```bash
uv run flowos_core serve my_flow.py
```

### Start with no flows

`flowos_core serve` starts with an empty registry when no flow path is provided. Flows can then be uploaded via the API:

```bash
uv run flowos_core serve --env-file .env
```

### Upload flows dynamically

While the server is running, upload flows with `POST /flows/upload/`.

The endpoint accepts the full FlowOS export JSON directly, the same format you get from the FlowOS UI's **Export** button:

```bash
# Upload a flow JSON file
curl -X POST http://localhost:8000/flows/upload/ \
  -H "x-api-key: $FLOWOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d @my-flow.json

# Upload and replace an existing flow with the same ID
curl -X POST "http://localhost:8000/flows/upload/?replace=true" \
  -H "x-api-key: $FLOWOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d @my-flow.json
```

The server returns a `409 Conflict` error if you upload a flow whose ID is already registered and `replace=true` is not set.

### Multi-worker deployment

Use `--workers N` to start multiple uvicorn worker processes, and `--flow-dir` to point all workers at a shared directory so they serve the same flows.

```bash
# 4 workers, flows shared via a local temp directory
uv run flowos_core serve flows/ --workers 4 --flow-dir /tmp/flowos_core-flows

# Cross-pod sharing (Kubernetes PVC or similar network volume)
uv run flowos_core serve flows/ --workers 4 --flow-dir /mnt/shared-flows
```

How it works:

- Each startup flow file is persisted to `--flow-dir` as `{flow_id}.json` when the server starts.
- Uploads via `POST /flows/upload/` are also written to `--flow-dir`, making them visible to every worker on the next request.
- Deletes propagate across workers: each worker detects a missing file on the next request to that flow and returns `404`.
- Without `--flow-dir`, each worker maintains an isolated in-memory registry. Uploads reach only the worker that received the request.

> **Note:** `--workers > 1` with `--flow-dir` does not support `.py` script flows — Python graphs cannot be serialized to the filesystem store.

A warning is printed when `--workers > 1` is used without `--flow-dir`, because in that case each worker has its own isolated in-memory registry.

### Isolate credentials with `--no-env-fallback` _(experimental)_

By default, `flowos_core serve` resolves component credentials from the process environment (`os.environ`). In multi-tenant deployments, this means every request shares the same credentials.

Use `--no-env-fallback` to disable process-environment fallback. With this flag set, credentials must be supplied per-request in the `global_vars` field of the request body:

```bash
uv run flowos_core serve my-flow.json --no-env-fallback --env-file .env
```

Pass per-request credentials in the `global_vars` map under `FLOWOS_REQUEST_VARIABLES`:

```bash
curl -X POST http://localhost:8000/flows/$FLOW_ID/run \
  -H "Content-Type: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY" \
  -d '{
    "input_value": "Hello world",
    "global_vars": {
      "FLOWOS_REQUEST_VARIABLES": {
        "OPENAI_API_KEY": "sk-per-request-key"
      }
    }
  }'
```

Credentials supplied in `FLOWOS_REQUEST_VARIABLES` are scoped to the current request using Python `contextvars`. FlowOS's built-in components do not write them to `os.environ`, so they do not bleed into other concurrent requests on the same worker. Custom components that explicitly write to `os.environ` are outside this guarantee.

### Check or upgrade flow compatibility at startup

Use `--upgrade-flow` to check compatibility between a flow and the current FLOWOS_CORE version before serving it. See [FLOWOS_CORE and FlowOS version compatibility](https://docs.flowos.org/flowos_core-compatibility) for details on the version model.

```bash
# Fail at startup if any component is incompatible
uv run flowos_core serve my-flow.json --upgrade-flow=check

# Apply safe upgrades in memory, then start serving
uv run flowos_core serve my-flow.json --upgrade-flow=safe
```

### FLOWOS_CORE serve options

| Option | Description |
|--------|--------------|
| `--check-variables` / `--no-check-variables` | Check global variables for environment compatibility. Default: `--check-variables`. |
| `--env-file` | Path to the `.env` file containing environment variables. |
| `--flow-dir` | Directory for the filesystem-backed flow store shared across workers. When set, startup flows and uploads are persisted here. |
| `--flow-json` | Read inline flow JSON content as a string. Example: `uv run flowos_core serve --flow-json '{...}'`. |
| `--host`, `-h` | Host to bind the server to. Default: `127.0.0.1`. |
| `--log-level` | Logging level. One of: `debug`, `info`, `warning`, `error`, `critical`. Default: `warning`. |
| `--no-env-fallback` / `--env-fallback` | Disable process-environment fallback for credential resolution. Use with per-request `FLOWOS_REQUEST_VARIABLES`. Default: `--env-fallback`. |
| `--port`, `-p` | Port to bind the server to. Default: `8000`. |
| `--stdin` | Read JSON flow content from `stdin`. Example: `cat flow.json | uv run flowos_core serve --stdin`. |
| `--upgrade-flow` | Compatibility mode: `check` reports issues and fails, `safe` applies safe upgrades in memory. |
| `--verbose`, `-v` | Show diagnostic output and execution details. |
| `--workers`, `-w` | Number of uvicorn worker processes. Default: `1`. Use with `--flow-dir` for multi-worker flow sharing. |

## Run the simple agent flow with `flowos_core run`

The `flowos_core run` command runs a flow from a JSON file without serving it, and the output is sent to `stdout`. Input to `flowos_core run` can be a path to the JSON file, inline JSON passed with `--input-value`, or read from `stdin`. No FlowOS API key is required.

This example uses the **Agent** component's built-in OpenAI model, which requires an OpenAI API key. If you want to use a different provider, edit the model provider, model name, and credentials accordingly.

1. Export your variables in the same terminal session where you'll run the flow:

   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

2. Install dependencies.

   If you already have FlowOS installed, or if you're running from source at `src/flowos-core`, FLOWOS_CORE is included with FlowOS and all dependencies are already available. You don't need to install additional dependencies.

   If you install the standalone `flowos_core` package from [PyPI](https://pypi.org/project/flowos_core/) or run FLOWOS_CORE with `uvx`, you need to manually install the dependencies required by the components in your flow.

   To find which dependencies your flow requires:

   1. Run your flow with [flowos_core run](#run-the-simple-agent-flow-with-flowos_core-run):

      ```bash
      uv run flowos_core run simple-agent-flow.json "test input"
      ```

      FLOWOS_CORE reports any missing dependencies in the subsequent error message.
   2. Install the missing dependencies that FLOWOS_CORE reports.

   For example, to run the simple agent template flow, install these dependencies in your environment before running the simple agent flow:

   ```bash
   uv pip install "langchain~=0.3.23" "langchain-core<1.0.0" "langchain-community" "langchain-openai" "langchain-text-splitters" beautifulsoup4 lxml requests
   ```

3. Run the flow from a flow JSON file:

   ```bash
   uv run flowos_core run simple-agent-flow.json "Hello world"
   ```

   This flow expects a `Message` input, which is a simple text string.

   You can also use the `--input-value` flag instead of a positional argument:

   ```bash
   uv run flowos_core run simple-agent-flow.json --input-value "Hello world"
   ```

   The `--input-value` flag is required when using `--stdin` or `--flow-json` options, since those options use the positional argument for the flow definition instead of the input value.

In addition to running flows from JSON files, `flowos_core run` supports other input methods, described below.

### Run flows from stdin

The `--stdin` option lets you run flows from dynamic sources (APIs, databases) or after modifying a flow before execution. The command reads the flow's JSON definition from `stdin`, validates the JSON structure, and runs the flow. The `--input-value` flag is required when using `--stdin`.

Read a flow JSON from stdin:

```bash
cat simple-agent-flow.json | uv run flowos_core run --stdin \
  --input-value "Hello world" \
  --format json | jq '.result'
```

Fetch a flow JSON from a remote API and run it:

```bash
curl https://api.example.com/flows/my-agent-flow | uv run flowos_core run --stdin \
  --input-value "Hello world"
```

Modify a flow created in the visual builder before execution (e.g. change the OpenAI model to `gpt-4o`):

```bash
cat simple-agent-flow.json | jq '(.data.nodes[] | select(.data.node.template.model_name.value) | .data.node.template.model_name.value) = "gpt-4o"' | \
  uv run flowos_core run --stdin \
  --input-value "Hello world" \
  --format json | jq '.result'
```

### Run flows with inline JSON

Instead of piping from `stdin` or reading from a JSON file, you can pass the flow JSON directly as a string argument. The `--input-value` flag is required when using `--flow-json`.

```bash
uv run flowos_core run --flow-json '{"data": {"nodes": [...], "edges": [...]}}' \
  --input-value "Hello world"
```

### FLOWOS_CORE run options

| Option | Description |
|--------|--------------|
| `--check-variables` / `--no-check-variables` | Validate the flow's global variables. Default: check. |
| `--flow-json` | Load inline JSON flow content as a string. |
| `--format`, `-f` | Output format. One of: `json`, `text`, `message`, `result`. Default: `json`. |
| `--input-value` | Input value to pass to the graph. |
| `--session-id` | Session ID for conversation tracking. Agent and Memory components use this to maintain history across runs. Auto-generated if not set. |
| `--stdin` | Read JSON flow content from `stdin`. |
| `--timing` | Include detailed timing information in output. |
| `--upgrade-flow` | Compatibility mode: `check` reports issues and fails, `safe` applies safe upgrades in memory before running. |
| `--verbose`, `-v` | Show basic progress and diagnostic output. |
| `-vv` | Show detailed progress and debug information. |
| `-vvv` | Show full debugging output including component logs. |

In addition to running flows from JSON files, you can use `flowos_core run` with Python scripts that define flows programmatically. This approach allows you to create flows directly in Python code without the visual builder.

For a complete example of creating an agent flow programmatically using FLOWOS_CORE components, see the [Complete Agent Example on PyPI](https://pypi.org/project/flowos_core) or the **Complete Agent Example** below.

#### Complete agent example

Create a file called `simple_agent.py`:

```python
"""A simple agent flow example for FlowOS.

Usage:
    uv run flowos_core run simple_agent.py "How are you?"
"""

import os
from pathlib import Path

from flowos_core import components as cp
from flowos_core.graph import Graph
from flowos_core.log.logger import LogConfig


async def get_graph() -> Graph:
    """Create and return the graph with async component initialization."""
    log_config = LogConfig(
        log_level="INFO",
        log_file=Path("flowos.log"),
    )

    chat_input = cp.ChatInput()
    agent = cp.AgentComponent()
    url_component = cp.URLComponent()
    tools = await url_component.to_toolkit()

    agent.set(
        model_name="gpt-4.1-mini",
        agent_llm="OpenAI",
        api_key=os.getenv("OPENAI_API_KEY"),
        input_value=chat_input.message_response,
        tools=tools,
    )
    chat_output = cp.ChatOutput().set(input_value=agent.message_response)

    return Graph(chat_input, chat_output, log_config=log_config)
```

Install dependencies and set your OpenAI API key, then run:

```bash
uv run flowos_core run simple_agent.py "How are you?" --verbose
```

## flowos-mcp

`flowos-mcp` is a separate binary installed with `flowos_core`. It starts an MCP server that gives any MCP-compatible client programmatic control over a FlowOS instance for building flows, managing components, and running executions.

For more information, see [FLOWOS_MCP.md](./FLOWOS_MCP.md).

## Development

```bash
# Install development dependencies
make dev

# Run tests
make test

# Format code
make format
```

## Pluggable services

FLOWOS_CORE supports a pluggable service architecture that lets you customize and extend its behavior. You can replace built-in services (storage, telemetry, tracing, etc.) with your own implementations or use FlowOS's full-featured services.

For more information, see [PLUGGABLE_SERVICES.md](./PLUGGABLE_SERVICES.md).

## Flattened component access

FLOWOS_CORE supports simplified component imports for a better developer experience when building flows in Python.
You get simpler imports, easier discovery via `cp.ComponentName`, and full backward compatibility with the traditional import method.

**Before (old import style):**

```python
from flowos_core.components.agents.agent import AgentComponent
from flowos_core.components.data.url import URLComponent
from flowos_core.components.input_output import ChatInput, ChatOutput
```

**Now (flattened style):**

```python
from flowos_core import components as cp

chat_input = cp.ChatInput()
agent = cp.AgentComponent()
url_component = cp.URLComponent()
chat_output = cp.ChatOutput()
```

## Component category allowlist and blocklist

You can restrict which component categories are available when loading flows by using an allowlist or a blocklist.

### Environment variables

Both settings are optional. When unset or empty, all categories from the component index are loaded.

| Variable | Description |
|----------|-------------|
| `FLOWOS_COMPONENT_CATEGORY_ALLOWLIST` | Comma-separated list of component category names to **include**. If empty (default), all categories are included. If set, only the listed categories are available. |
| `FLOWOS_COMPONENT_CATEGORY_BLOCKLIST` | Comma-separated list of component category names to **exclude**. If empty (default), no categories are excluded. Applied after the allowlist. |

Category names are case-insensitive.

### Component categories

Category names in the allowlist and blocklist match the component index (e.g. top-level folders under `flowos_core.components`). The virtual keyword **`core`** in the allowlist or blocklist expands to the following core categories (aligned with the frontend sidebar):

- `input_output`, `data_source`, `models_and_agents`, `llm_operations`, `files_and_knowledge`, `processing`, `flow_controls`, `utilities`, `prototypes`, `tools`, `agents`, `data`, `logic`, `helpers`, `models`, `vectorstores`, `inputs`, `outputs`, `prompts`, `chains`, `documentloaders`, `link_extractors`, `output_parsers`, `retrievers`, `textsplitters`, `toolkits`

Provider-specific and other categories (e.g. `openai`, `anthropic`, `google`, `langchain_utilities`) are also valid; the full set depends on your FLOWOS_CORE version and index.

### How to use in FLOWOS_CORE

1. Set one or both environment variables before running `flowos_core serve` or `flowos_core run`. The filter is applied when the component index is loaded.

Allowlist only — restrict to specific categories:

   ```bash
   export FLOWOS_COMPONENT_CATEGORY_ALLOWLIST="openai,anthropic,google,processing,input_output"
   uv run flowos_core serve my_flow.json
   ```

Blocklist only — load all categories except the ones you exclude:

   ```bash
   export FLOWOS_COMPONENT_CATEGORY_BLOCKLIST="prototypes,langchain_utilities"
   uv run flowos_core run my_flow.json "Hello"
   ```

Virtual `core` keyword — use `core` in the allowlist or blocklist to refer to all core categories at once (e.g. allow only core categories, or exclude all core from a broader set):

   ```bash
   export FLOWOS_COMPONENT_CATEGORY_ALLOWLIST="core"
   uv run flowos_core serve my_flow.json
   ```

## License

MIT License. See [LICENSE](../../LICENSE) for details.
