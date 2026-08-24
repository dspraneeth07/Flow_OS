"""Database service constants."""

# Minimum PostgreSQL major version required by FlowOS.
# The schema uses UNIQUE NULLS DISTINCT, which is only supported in PostgreSQL 15+.
MIN_POSTGRESQL_MAJOR_VERSION = 15

# User-facing message when migrations fail due to PostgreSQL < 15 (e.g. UNIQUE NULLS DISTINCT).
POSTGRESQL_VERSION_REQUIRED_MESSAGE = (
    f"FlowOS requires PostgreSQL {MIN_POSTGRESQL_MAJOR_VERSION} or higher when using PostgreSQL as the database. "
    "The current PostgreSQL version does not support the syntax used by FlowOS's schema. "
    f"Please upgrade your PostgreSQL instance to version {MIN_POSTGRESQL_MAJOR_VERSION} or higher. "
    "See: https://docs.flowos.org/configuration-custom-database"
)
