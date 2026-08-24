# Running FlowOS with Docker

This guide will help you get FlowOS up and running using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Steps

1. Clone the FlowOS repository:

   ```sh
   git clone https://github.com/flowos-ai/flowos.git
   ```

2. Navigate to the `docker_example` directory:

   ```sh
   cd flowos/docker_example
   ```

3. Create a `.env` file with the FlowOS admin password:

   ```sh
   FLOWOS_SUPERUSER_PASSWORD=replace-with-a-strong-password
   ```

   The default admin username is `flowos`.

4. Run the Docker Compose file:

   ```sh
   docker compose up
   ```

FlowOS will now be accessible at [http://localhost:7860/](http://localhost:7860/).

## Docker Compose Configuration

The Docker Compose configuration spins up two services: `flowos` and `postgres`.

### FlowOS Service

The `flowos` service uses the `flowosai/flowos:latest` Docker image and exposes port 7860. It depends on the `postgres` service.

Environment variables:

- `FLOWOS_DATABASE_URL`: The connection string for the PostgreSQL database.
- `FLOWOS_SUPERUSER_PASSWORD`: The initial admin password. This value is required in `.env`.
- `FLOWOS_CONFIG_DIR`: The directory where FlowOS stores logs, file storage, monitor data, and secret keys.

Volumes:

- `flowos-data`: This volume is mapped to `/app/flowos` in the container.

### PostgreSQL Service

The `postgres` service uses the `postgres:16-trixie` Docker image and exposes port 5432. The image is pinned to a specific Debian base (`trixie`, Debian 13) so the `postgres:16` tag cannot silently roll its underlying OS, which would otherwise produce a glibc collation version mismatch warning on existing data volumes.

Environment variables:

- `POSTGRES_USER`: The username for the PostgreSQL database.
- `POSTGRES_PASSWORD`: The password for the PostgreSQL database.
- `POSTGRES_DB`: The name of the PostgreSQL database.

Volumes:

- `flowos-postgres`: This volume is mapped to `/var/lib/postgresql/data` in the container.

### Upgrading from a `bookworm`-initialized volume

Earlier versions of this example used `postgres:16`, which initially shipped on Debian Bookworm (glibc 2.36). The pinned image now uses Trixie (glibc 2.41). On the first start against a volume that was initialized under Bookworm, PostgreSQL logs a one-time warning:

```
WARNING: database "flowos" has a collation version mismatch
DETAIL: The database was created using collation version 2.36, but the operating system provides version 2.41.
```

To clear it, refresh the collation version against the running database (one-off, takes seconds on a typical FlowOS database):

```sh
docker compose exec postgres \
  psql -U flowos -d flowos \
  -c "REINDEX DATABASE flowos;" \
  -c "ALTER DATABASE flowos REFRESH COLLATION VERSION;"
```

Fresh installs are unaffected.

## Switching to a Specific FlowOS Version

If you want to use a specific version of FlowOS, you can modify the `image` field under the `flowos` service in the Docker Compose file. For example, to use version 1.0-alpha, change `flowosai/flowos:latest` to `flowosai/flowos:1.0-alpha`.
