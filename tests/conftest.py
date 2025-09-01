# tests/conftest.py
import os
import pytest
from app.services.indexer import INDEX_FILE

@pytest.fixture(autouse=True)
def cleanup_index():
    # cleanup before each test
    if os.path.exists(INDEX_FILE):
        os.remove(INDEX_FILE)
    yield
    # cleanup after each test (just in case)
    if os.path.exists(INDEX_FILE):
        os.remove(INDEX_FILE)