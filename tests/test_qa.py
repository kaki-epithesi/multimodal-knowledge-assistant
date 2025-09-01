import os
from fastapi.testclient import TestClient
from app.main import app
from app.services.indexer import INDEX_FILE

client = TestClient(app)


def test_query_no_index():
    # Ensure index file is deleted before test
    if os.path.exists(INDEX_FILE):
        os.remove(INDEX_FILE)

    resp = client.post("/query", json={"q": "hello"})
    # Now we expect 404 because no index exists
    assert resp.status_code == 404