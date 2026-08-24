#!/usr/bin/env bash
# FlowOS self-extracting installer (Linux, x86_64).
#
# This file is a normal shell script with three sections appended after the
# __ARCHIVE_BELOW__ marker: a gzipped tar of a portable CPython build, a
# gzipped tar of the `flowos` package + its dependencies, and a plain-text
# copy of launcher.sh. On first run it extracts the two archives into
# ~/.local/share/FlowOS (skipped on later runs if already present), then
# runs launcher.sh, which starts the server and opens the browser.
set -u

INSTALL_DIR="${FLOWOS_INSTALL_DIR:-$HOME/.local/share/FlowOS}"
PYTHON_TAR_SIZE=__PYTHON_TAR_SIZE__
PAYLOAD_TAR_SIZE=__PAYLOAD_TAR_SIZE__

SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
MARKER_LINE=$(awk '/^__ARCHIVE_BELOW__$/ { print NR + 1; exit 0; }' "$SELF")

if [ ! -x "$INSTALL_DIR/runtime/python/bin/python3.11" ]; then
    echo "Installing FlowOS to $INSTALL_DIR (this includes ~3GB of AI/ML libraries, first run only)..."
    mkdir -p "$INSTALL_DIR/runtime/python/lib/python3.11/site-packages"

    echo "Extracting Python runtime..."
    tail -n "+$MARKER_LINE" "$SELF" | head -c "$PYTHON_TAR_SIZE" | tar xz -C "$INSTALL_DIR/runtime"

    echo "Extracting FlowOS and its dependencies (this is the slow part)..."
    tail -n "+$MARKER_LINE" "$SELF" | tail -c "+$((PYTHON_TAR_SIZE + 1))" | head -c "$PAYLOAD_TAR_SIZE" \
        | tar xz -C "$INSTALL_DIR/runtime/python/lib/python3.11/site-packages"
fi

tail -n "+$MARKER_LINE" "$SELF" | tail -c "+$((PYTHON_TAR_SIZE + PAYLOAD_TAR_SIZE + 1))" > "$INSTALL_DIR/launcher.sh"
chmod +x "$INSTALL_DIR/launcher.sh"

exec "$INSTALL_DIR/launcher.sh"
__ARCHIVE_BELOW__
