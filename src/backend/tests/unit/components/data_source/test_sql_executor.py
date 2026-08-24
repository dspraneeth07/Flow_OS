import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from flowos_core.components.data_source.sql_executor import SQL_DATABASE_ENGINE_ARGS, SQLComponent
from flowos_core.schema import DataFrame, Message
from flowos_core.services.cache.utils import CacheMiss

from tests.base import ComponentTestBaseWithoutClient


class FakeSharedComponentCache:
    def __init__(self, values=None):
        self.values = values or {}

    def get(self, key):
        return self.values.get(key, CacheMiss())

    def set(self, key, value):
        self.values[key] = value


class TestSQLComponent(ComponentTestBaseWithoutClient):
    @pytest.fixture
    def test_db(self, tmp_path: Path):
        """Fixture that creates a temporary SQLite database for testing.

        Uses tmp_path rather than a fixed file under tests/data: that path was
        shared by every test and every xdist worker, so parallel runs collided
        on `INSERT id=1` (UNIQUE constraint failed: test.id), and a killed run
        left the file behind to poison the next one. tmp_path is unique per test
        and cleaned up by pytest even if the run dies.
        """
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO test (id, name)
            VALUES (1, 'name_test')
        """)
        conn.commit()
        conn.close()
        return str(db_path)

    @pytest.fixture
    def component_class(self):
        """Return the component class to test."""
        return SQLComponent

    @pytest.fixture
    def default_kwargs(self, test_db):
        """Return the default kwargs for the component."""
        return {
            "database_url": f"sqlite:///{test_db}",
            "query": "SELECT * FROM test",
            "include_columns": True,
            "add_error": False,
        }

    @pytest.fixture
    def file_names_mapping(self):
        """Return an empty list since this component doesn't have version-specific files."""
        return []

    def test_successful_query_with_columns(self, component_class: type[SQLComponent], default_kwargs):
        """Test a successful SQL query with columns included."""
        component = component_class(**default_kwargs)

        result = component.build_component()

        assert isinstance(result, Message)
        assert isinstance(result.text, str)
        assert result.text == "[{'id': 1, 'name': 'name_test'}]"

    def test_successful_query_without_columns(self, component_class: type[SQLComponent], default_kwargs):
        """Test a successful SQL query without columns included."""
        default_kwargs["include_columns"] = False
        component = component_class(**default_kwargs)

        result = component.build_component()

        assert isinstance(result, Message)
        assert isinstance(result.text, str)
        assert result.text == "[(1, 'name_test')]"
        assert component.status == "[(1, 'name_test')]"
        assert component.query == "SELECT * FROM test"

    def test_query_error_with_add_error(self, component_class: type[SQLComponent], default_kwargs):
        """Test a SQL query that raises an error with add_error=True."""
        default_kwargs["add_error"] = True
        default_kwargs["query"] = "SELECT * FROM non_existent_table"
        component = component_class(**default_kwargs)

        result = component.build_component()

        assert isinstance(result, Message)
        assert isinstance(result.text, str)
        assert "no such table: non_existent_table" in result.text
        assert "Error:" in result.text
        assert "Query: SELECT * FROM non_existent_table" in result.text

    def test_run_sql_query(self, component_class: type[SQLComponent], default_kwargs):
        """Test building a DataFrame from a SQL query."""
        component = component_class(**default_kwargs)

        result = component.run_sql_query()

        assert isinstance(result, DataFrame)
        assert len(result) == 1
        assert "id" in result.columns
        assert "name" in result.columns
        assert result.iloc[0]["id"] == 1
        assert result.iloc[0]["name"] == "name_test"

    def test_maybe_create_db_reuses_cached_database(self, component_class: type[SQLComponent], default_kwargs):
        """Test cached database reuse without creating a new engine."""
        cached_db = Mock()
        cache = FakeSharedComponentCache({default_kwargs["database_url"]: cached_db})
        component = component_class(**default_kwargs)
        component._shared_component_cache = cache

        with patch("flowos_core.components.data_source.sql_executor.SQLDatabase.from_uri") as mock_from_uri:
            component.maybe_create_db()

        assert component.db is cached_db
        mock_from_uri.assert_not_called()

    def test_maybe_create_db_enables_pool_pre_ping(self, component_class: type[SQLComponent], default_kwargs):
        """Test new cached databases validate stale pooled connections on checkout."""
        created_db = Mock()
        cache = FakeSharedComponentCache()
        component = component_class(**default_kwargs)
        component._shared_component_cache = cache

        with patch(
            "flowos_core.components.data_source.sql_executor.SQLDatabase.from_uri",
            return_value=created_db,
        ) as mock_from_uri:
            component.maybe_create_db()

        mock_from_uri.assert_called_once_with(default_kwargs["database_url"], engine_args=SQL_DATABASE_ENGINE_ARGS)
        assert component.db is created_db
        assert cache.values[default_kwargs["database_url"]] is created_db
