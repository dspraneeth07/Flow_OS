FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim
ENV TZ=UTC

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    curl \
    npm \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

# Install dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=README.md,target=README.md \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=src/backend/base/README.md,target=src/backend/base/README.md \
    --mount=type=bind,source=src/backend/base/pyproject.toml,target=src/backend/base/pyproject.toml \
    --mount=type=bind,source=src/flowos-core/README.md,target=src/flowos-core/README.md \
    --mount=type=bind,source=src/flowos-core/pyproject.toml,target=src/flowos-core/pyproject.toml \
    --mount=type=bind,source=src/sdk/README.md,target=src/sdk/README.md \
    --mount=type=bind,source=src/sdk/pyproject.toml,target=src/sdk/pyproject.toml \
    --mount=type=bind,source=src/bundles,target=src/bundles \
    uv sync --frozen --no-install-project --no-dev --extra postgresql

EXPOSE 7860
EXPOSE 3000

CMD ["./docker/dev.start.sh"]
