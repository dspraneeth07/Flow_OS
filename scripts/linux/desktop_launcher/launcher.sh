#!/usr/bin/env bash
# FlowOS Desktop launcher (Linux).
#
# Runs the bundled flowos server out of the runtime/ folder that sits next to
# this script (placed there by the self-extracting installer), waits for it
# to become healthy, and opens it in the default browser.
#
# Kept to plain bash + coreutils on purpose: no GUI toolkit dependency, so it
# works the same whether a desktop environment is present or not.
set -u

APP_NAME="FlowOS"
DEFAULT_PORT=7860
HEALTH_TIMEOUT_SECONDS=300

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$SCRIPT_DIR/runtime"
DATA_DIR="$SCRIPT_DIR/data"
LOG_PATH="$SCRIPT_DIR/launcher.log"
PYTHON_BIN="$RUNTIME_DIR/python/bin/python3.11"

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG_PATH"
}

fatal() {
    log "FATAL: $1"
    echo "FlowOS failed to start: $1" >&2
    echo "See $LOG_PATH for details." >&2
    exit 1
}

if [ ! -x "$PYTHON_BIN" ]; then
    fatal "FlowOS runtime not found at $PYTHON_BIN. Reinstall FlowOS."
fi

mkdir -p "$DATA_DIR"

find_free_port() {
    local port=$1
    while (echo >/dev/tcp/127.0.0.1/"$port") 2>/dev/null; do
        port=$((port + 1))
    done
    echo "$port"
}

PORT=$(find_free_port "$DEFAULT_PORT")

echo "Starting FlowOS (first launch can take a minute)..."
log "Starting flowos on port $PORT"

(
    cd "$DATA_DIR" || exit 1
    exec "$PYTHON_BIN" -m flowos run --host 127.0.0.1 --port "$PORT" >> "$LOG_PATH" 2>&1
) &
SERVER_PID=$!

echo "$SERVER_PID" > "$SCRIPT_DIR/flowos.pid"

open_browser() {
    local url=$1
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$url" >/dev/null 2>&1 &
    elif command -v gio >/dev/null 2>&1; then
        gio open "$url" >/dev/null 2>&1 &
    elif command -v sensible-browser >/dev/null 2>&1; then
        sensible-browser "$url" >/dev/null 2>&1 &
    else
        echo "Open $url in your browser."
    fi
}

deadline=$(( $(date +%s) + HEALTH_TIMEOUT_SECONDS ))
while [ "$(date +%s)" -lt "$deadline" ]; do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        fatal "FlowOS server exited unexpectedly. See $LOG_PATH for details."
    fi
    if command -v curl >/dev/null 2>&1; then
        if curl -sf -o /dev/null "http://127.0.0.1:$PORT/health"; then
            echo "FlowOS is running at http://127.0.0.1:$PORT"
            open_browser "http://127.0.0.1:$PORT"
            echo "Press Ctrl+C to stop FlowOS."
            wait "$SERVER_PID"
            exit 0
        fi
    elif command -v wget >/dev/null 2>&1; then
        if wget -q -O /dev/null "http://127.0.0.1:$PORT/health"; then
            echo "FlowOS is running at http://127.0.0.1:$PORT"
            open_browser "http://127.0.0.1:$PORT"
            echo "Press Ctrl+C to stop FlowOS."
            wait "$SERVER_PID"
            exit 0
        fi
    fi
    sleep 1
done

fatal "FlowOS did not become ready within $HEALTH_TIMEOUT_SECONDS seconds."
