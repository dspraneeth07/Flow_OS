# CI/CD Pipeline Templates

Ready-to-use workflow files for the Flow DevOps Toolkit.
Copy the files you need into your project's CI configuration.

## GitHub Actions

| File | Trigger | Secrets needed |
|------|---------|----------------|
| [`github-actions/flowos-validate.yml`](github-actions/flowos-validate.yml) | PR touching `flows/**/*.json` | None |
| [`github-actions/flowos-test.yml`](github-actions/flowos-test.yml) | PR touching flows or tests | `FLOWOS_STAGING_API_KEY` |
| [`github-actions/flowos-push.yml`](github-actions/flowos-push.yml) | Push to `main` touching flows | `FLOWOS_PROD_API_KEY` |

### Quick start

```bash
mkdir -p .github/workflows
cp github-actions/flowos-validate.yml \
   github-actions/flowos-test.yml \
   github-actions/flowos-push.yml \
   .github/workflows/
```

Configure these in **Settings → Environments**:

**`staging`** environment (used by `flowos-test.yml`):
| Name | Type | Value |
|------|------|-------|
| `FLOWOS_STAGING_URL` | Variable | `https://staging.flowos.example.com` |
| `FLOWOS_STAGING_API_KEY` | Secret | your staging API key |

**`production`** environment (used by `flowos-push.yml`):
| Name | Type | Value |
|------|------|-------|
| `FLOWOS_PROD_URL` | Variable | `https://flowos.example.com` |
| `FLOWOS_PROD_API_KEY` | Secret | your production API key |
| `FLOWOS_PROJECT_NAME` | Variable | `Production Flows` *(optional)* |

Add **Required reviewers** to the `production` environment to gate every deploy
behind a manual approval step.

---

## GitLab CI

| File | Description |
|------|-------------|
| [`gitlab-ci/flowos.yml`](gitlab-ci/flowos.yml) | Three-stage template: validate → test → deploy |

### Quick start

```bash
mkdir -p .gitlab/ci
cp gitlab-ci/flowos.yml .gitlab/ci/
```

Add to your `.gitlab-ci.yml`:

```yaml
include:
  - local: .gitlab/ci/flowos.yml
```

Configure these in **Settings → CI/CD → Variables**:

| Variable | Protected | Masked | Description |
|----------|-----------|--------|-------------|
| `FLOWOS_STAGING_URL` | ✓ | ✗ | Staging instance URL |
| `FLOWOS_STAGING_API_KEY` | ✓ | ✓ | Staging API key |
| `FLOWOS_PROD_URL` | ✓ | ✗ | Production instance URL |
| `FLOWOS_PROD_API_KEY` | ✓ | ✓ | Production API key |
| `FLOWOS_PROJECT_NAME` | ✗ | ✗ | Project folder name *(optional)* |

---

## Shell scripts (`ci/`)

The `shell/` templates (`ci-validate.sh`, `ci-test.sh`, `ci-push.sh`) work with
any CI system (Jenkins, CircleCI, Bitbucket Pipelines, Azure Pipelines, etc.).
They are copied to `ci/` by `flowos_core init`.

### Environment variables

#### `ci-validate.sh`

| Variable | Default | Description |
|----------|---------|-------------|
| `FLOWS_DIR` | `flows/` | Directory containing flow JSON files |
| `VALIDATE_LEVEL` | `4` | Validation depth (1–4) |
| `VALIDATE_FORMAT` | `text` | Output format: `text` or `json` |
| `FLOWOS_VERSION` | *(latest)* | PEP 508 version specifier for `flowos_core`, e.g. `>=0.4,<1` or `==1.2.3` |

#### `ci-test.sh`

| Variable | Default | Description |
|----------|---------|-------------|
| `FLOWOS_URL` | — | URL of target FlowOS instance (Approach A) |
| `FLOWOS_API_KEY` | — | API key for target instance (Approach A) |
| `FLOWOS_ENV` | — | Environment name from config (Approach B) |
| `FLOWOS_ENVIRONMENTS_FILE` | `flowos-environments.toml` | Path to environments config (Approach B) |
| `TESTS_DIR` | `tests/` | Directory containing test files |
| `PYTEST_MARKERS` | `integration` | Markers passed to `pytest -m` |
| `PYTEST_ARGS` | — | Extra arguments forwarded verbatim to pytest |
| `SDK_VERSION` | *(latest)* | PEP 508 version specifier for `flowos-sdk` |

#### `ci-push.sh`

| Variable | Default | Description |
|----------|---------|-------------|
| `FLOWOS_URL` | — | URL of target FlowOS instance (Approach A) |
| `FLOWOS_API_KEY` | — | API key for target instance (Approach A) |
| `FLOWOS_ENV` | — | Environment name from config (Approach B) |
| `FLOWOS_ENVIRONMENTS_FILE` | `flowos-environments.toml` | Path to environments config (Approach B) |
| `FLOWS_DIR` | `flows/` | Directory containing flow JSON files |
| `FLOWOS_PROJECT` | — | Project (folder) name on the remote instance |
| `FLOWOS_PROJECT_ID` | — | Project UUID (takes precedence over `FLOWOS_PROJECT`) |
| `DRY_RUN` | `false` | Set to `true` to preview without making changes |
| `FLOWOS_VERSION` | *(latest)* | PEP 508 version specifier for `flowos_core` |

---

## How it all fits together

```
PR opened
  │
  ├── flowos-validate  ──── flowos_core validate flows/ --level 4
  │                           ↳ blocks merge if any flow is malformed
  │
  └── flowos-test  ──────── pytest tests/ --flowos-env staging
                              ↳ skips gracefully if staging is unavailable

Merge to main
  │
  └── flowos-push  ──────── flowos_core push --dir flows/ --env production
                              ↳ upserts every flow by stable ID
                              ↳ idempotent: safe to re-run
```

## Writing integration tests

Install the testing extra:

```bash
pip install "flowos-sdk[testing]"
```

Create `tests/test_flows.py`:

```python
def test_rag_flow(flow_runner):
    response = flow_runner("rag-endpoint", "What is FlowOS?")
    assert "FlowOS" in response.first_text_output()

async def test_async_flow(async_flow_runner):
    response = await async_flow_runner("my-endpoint", "Hello!")
    assert response.first_text_output() is not None
```

Run locally against staging:

```bash
FLOWOS_URL=https://staging.flowos.example.com \
FLOWOS_API_KEY=<key> \
pytest tests/ -m integration
```
