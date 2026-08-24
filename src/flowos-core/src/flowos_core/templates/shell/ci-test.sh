#!/usr/bin/env bash
# ci-test.sh
#
# PURPOSE
#   Run pytest flow-integration tests against a live FlowOS instance
#   using the flowos-sdk `flow_runner` fixture.
#
# USAGE
#   chmod +x ci-test.sh
#   ./ci-test.sh
#
# ENVIRONMENT VARIABLES — connection (pick one approach)
#
#   Approach A: direct URL + key (simplest)
#     FLOWOS_URL        URL of the target FlowOS instance.
#                         e.g. https://staging.flowos.example.com
#     FLOWOS_API_KEY    API key for that instance.
#
#   Approach B: named environment from a TOML config
#     FLOWOS_ENV                 Name of the environment block in the TOML.
#                                  e.g. staging
#     FLOWOS_ENVIRONMENTS_FILE   Path to the environments TOML.
#                                  Default: flowos-environments.toml
#     <api_key_env var>            The env var named in api_key_env inside the
#                                  TOML block, e.g. FLOWOS_STAGING_API_KEY.
#
#   The TOML format (see also ci-push.sh):
#
#     [environments.staging]
#     url        = "https://staging.flowos.example.com"
#     api_key_env = "FLOWOS_STAGING_API_KEY"
#
# ENVIRONMENT VARIABLES — behaviour
#   TESTS_DIR        Directory containing test files.  Default: tests/
#   PYTEST_MARKERS   Markers to pass to -m.  Default: integration
#   PYTEST_ARGS      Extra arguments forwarded verbatim to pytest.
#   SDK_VERSION      flowos-sdk PEP 508 version specifier suffix appended
#                    directly to the package name, e.g. ">=0.4,<1" or "==1.2.3".
#                    Default: installs latest.
#
# SKIPPING
#   When neither FLOWOS_URL nor FLOWOS_ENV is set the tests auto-skip
#   (the flow_runner fixture detects no connection).  This means the script
#   exits 0 even when run on a branch that lacks the necessary secrets.
#
# EXIT CODES
#   0  All tests passed (or skipped due to missing connection)
#   1  One or more tests failed
#
# INTEGRATIONS
#   Jenkins:          sh 'ci-test.sh'
#   CircleCI:         - run: bash ci-test.sh
#   Bitbucket:        - bash ci-test.sh
#   Azure Pipelines:  - script: bash ci-test.sh

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────── #

TESTS_DIR="${TESTS_DIR:-tests/}"
PYTEST_MARKERS="${PYTEST_MARKERS:-integration}"
PYTEST_ARGS="${PYTEST_ARGS:-}"
SDK_VERSION="${SDK_VERSION:-}"
FLOWOS_ENV="${FLOWOS_ENV:-}"
FLOWOS_ENVIRONMENTS_FILE="${FLOWOS_ENVIRONMENTS_FILE:-flowos-environments.toml}"

# ── Install dependencies ───────────────────────────────────────────────────── #

# Normalise SDK_VERSION: if it looks like a bare version (starts with a digit),
# prepend "==" so the pip specifier is valid.
if [[ -n "${SDK_VERSION}" && "${SDK_VERSION}" =~ ^[0-9] ]]; then
  SDK_VERSION="==${SDK_VERSION}"
fi

echo "==> Installing flowos-sdk[testing] and pytest ..."
pip install --quiet \
  "flowos-sdk[testing]${SDK_VERSION}" \
  pytest

# ── Build environments file if using Approach B ───────────────────────────── #

if [[ -n "${FLOWOS_ENV}" && ! -f "${FLOWOS_ENVIRONMENTS_FILE}" ]]; then
  # Derive variable names from the env name (uppercased, hyphens → underscores)
  ENV_UPPER="${FLOWOS_ENV^^}"
  ENV_UPPER="${ENV_UPPER//-/_}"
  URL_VAR="FLOWOS_${ENV_UPPER}_URL"
  KEY_VAR="FLOWOS_${ENV_UPPER}_API_KEY"

  echo "==> Writing ${FLOWOS_ENVIRONMENTS_FILE} for environment '${FLOWOS_ENV}' ..."
  printf '[environments.%s]\nurl = "%s"\napi_key_env = "%s"\n' \
    "${FLOWOS_ENV}" \
    "${!URL_VAR:-}" \
    "${KEY_VAR}" \
    > "${FLOWOS_ENVIRONMENTS_FILE}"
fi

# ── Run tests ─────────────────────────────────────────────────────────────── #

# Build pytest command
PYTEST_CMD=(pytest "${TESTS_DIR}" -v --tb=short)

if [[ -n "${PYTEST_MARKERS}" ]]; then
  PYTEST_CMD+=(-m "${PYTEST_MARKERS}")
fi

if [[ -n "${FLOWOS_ENV}" ]]; then
  PYTEST_CMD+=(--flowos-env "${FLOWOS_ENV}")
  export FLOWOS_ENVIRONMENTS_FILE
elif [[ -n "${FLOWOS_URL:-}" ]]; then
  PYTEST_CMD+=(--flowos-url "${FLOWOS_URL}")
  [[ -n "${FLOWOS_API_KEY:-}" ]] && PYTEST_CMD+=(--flowos-api-key "${FLOWOS_API_KEY}")
fi

# Append any extra user-supplied args
# shellcheck disable=SC2206
[[ -n "${PYTEST_ARGS}" ]] && PYTEST_CMD+=(${PYTEST_ARGS})

echo "==> Running: ${PYTEST_CMD[*]}"
"${PYTEST_CMD[@]}"
