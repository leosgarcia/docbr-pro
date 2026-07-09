import os
import tempfile
from collections.abc import Generator

import pytest

from docbr_pro.enrichment.cache import CNPJCache


@pytest.fixture
def cache_db() -> Generator[str, None, None]:
    """Provides a temporary SQLite database file for testing."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


def test_cache_set_and_get(cache_db: str) -> None:
    """Test setting and getting values from the SQLite cache."""
    cache = CNPJCache(db_path=cache_db)

    # Not found
    assert cache.get("123") is None

    # Store and retrieve
    data = {"razao_social": "TESTE LTDA"}
    cache.set("123", data)

    retrieved = cache.get("123")
    assert retrieved is not None
    assert retrieved["razao_social"] == "TESTE LTDA"


def test_cache_overwrite(cache_db: str) -> None:
    """Test that setting an existing key overwrites the data."""
    cache = CNPJCache(db_path=cache_db)
    cache.set("123", {"status": "OLD"})
    cache.set("123", {"status": "NEW"})

    retrieved = cache.get("123")
    assert retrieved is not None
    assert retrieved["status"] == "NEW"
