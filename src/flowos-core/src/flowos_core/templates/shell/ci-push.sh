#!/usr/bin/env bash
# ci-push.sh
#
# PURPOSE
#   Push (upsert) FlowOS flow JSON files to a remote FlowOS instance
#   using `flowos_core push`.  Stable flow IDs mean re-running always converges.
#
# USAGE
#   chmod +x ci-push.sh
#   export FLOWOS_URL=https://staging.flowos.example.com
#   export FLOWOS_API_KEY=<your-api-key>
#   ./ci-push.sh
#
# ENVIRONMENT VARIABLES — connection (pick one approach)
#
#   Approach A: direct URL + key (simplest)
#     FLOWOS_URL        URL of the target FlowOS instance.
#     FLOWOS_API_KEY    API key for that instance.
#
#   Approach B: named environment from a TOML config
#     FLOWOS_ENV                 Name of the environment block.
#                                  e.g. staging  or  production
#     FLOWOS_ENVIRONMENTS_FILE   Path to environments TOML.
#                                  Default: flowos-environments.toml
#     <api_key_env var>            The env var named in api_key_env inside the
#                                  TOML block.  Must be exported separately.
#
#   The TOML format:
#
#     [environments.staging]
#     url         = "https://staging.flowos.example.com"
#     api_key_env  = "FLOWOS_STAGING_API_KEY"
#
#     [environments.production]
#     url         = "https://flowos.example.com"
#     api_key_env  = "FLOWOS_PROD_API_KEY"
#
# ENVIRONMENT VARIABLES — behaviour
#   FLOWS_DIR            Directory containing flow JSON files.
#                        Default: flows/
#   FLOWOS_PROJECT     Project (folder) name on the remote instance.
#                        Default: (no project — flows go to the default folder)
#   FLOWOS_PROJECT_ID  Project UUID.  Takes precedence over FLOWOS_PROJECT.
#   DRY_RUN              Set to "true" to show what would be pushed without
#                        making any changes.  Default: false
#   FLOWOS_VERSION          flowos_core PEP 508 version specifier suffix appended directly
#                        to the package name, e.g. ">=0.4,<1" or "==1.2.3".
#                        Default: installs latest.
#
# EXIT CODES
#   0  All flows pushed (or dry-run completed) successfully
#   1  One or more flows failed to push
#
# INTEGRATIONS
#   Jenkins:          sh 'ci-push.sh'
#   CircleCI:         - run: bash ci-push.sh
#   Bitbucket:        - bash ci-push.sh
#   Azure Pipelines:  - script: bash ci-push.sh

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────── #

FLOWS_DIR="${FLOWS_DIR:-flows/}"
FLOWOS_ENV="${FLOWOS_ENV:-}"
FLOWOS_ENVIRONMENTS_FILE="${FLOWOS_ENVIRONMENTS_FILE:-flowos-environments.toml}"
FLOWOS_URL="${FLOWOS_URL:-}"
FLOWOS_API_KEY="${FLOWOS_API_KEY:-}"
FLOWOS_PROJECT="${FLOWOS_PROJECT:-}"
FLOWOS_PROJECT_ID="${FLOWOS_PROJECT_ID:-}"
DRY_RUN="${DRY_RUN:-false}"
FLOWOS_VERSION="${FLOWOS_VERSION:-}"

# Normalise FLOWOS_VERSION: if it looks like a bare version (starts with a digit),
# prepend "==" so the pip specifier is valid.
if [[ -n "${FLOWOS_VERSION}" && "${FLOWOS_VERSION}" =~ ^[0-9] ]]; then
  FLOWOS_VERSION="==${FLOWOS_VERSION}"
fi

# ── Install flowos_core ───────────────────────────────────────────────────────────── #

echo "==> Installing flowos_core${FLOWOS_VERSION:+ ${FLOWOS_VERSION}} ..."
pip install --quiet "flowos_core${FLOWOS_VERSION}" flowos-sdk

# ── Build environments file if using Approach B ───────────────────────────── #

if [[ -n "${FLOWOS_ENV}" && ! -f "${FLOWOS_ENVIRONMENTS_FILE}" ]]; then
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
  export FLOWOS_ENVIRONMENTS_FILE
fi

# ── Build flowos_core push command ────────────────────────────────────────────────── #

PUSH_CMD=(flowos_core push --dir "${FLOWS_DIR}")

if [[ -n "${FLOWOS_ENV}" ]]; then
  PUSH_CMD+=(--env "${FLOWOS_ENV}")
elif [[ -n "${FLOWOS_URL}" ]]; then
  PUSH_CMD+=(--target "${FLOWOS_URL}")
  [[ -n "${FLOWOS_API_KEY}" ]] && PUSH_CMD+=(--api-key "${FLOWOS_API_KEY}")
else
  echo "ERROR: set FLOWOS_ENV (Approach B) or FLOWOS_URL (Approach A)" >&2
  exit 1
fi

if [[ -n "${FLOWOS_PROJECT_ID}" ]]; then
  PUSH_CMD+=(--project-id "${FLOWOS_PROJECT_ID}")
elif [[ -n "${FLOWOS_PROJECT}" ]]; then
  PUSH_CMD+=(--project "${FLOWOS_PROJECT}")
fi

[[ "${DRY_RUN}" == "true" ]] && PUSH_CMD+=(--dry-run)

# ── Push ──────────────────────────────────────────────────────────────────── #

echo "==> Pushing flows from ${FLOWS_DIR} ..."
[[ "${DRY_RUN}" == "true" ]] && echo "    (dry run — no changes will be made)"
echo "==> Running: ${PUSH_CMD[*]}"
"${PUSH_CMD[@]}"

echo "==> Done."
