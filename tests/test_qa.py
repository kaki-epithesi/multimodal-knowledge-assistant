from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_query_no_index():
    resp = client.post("/query", json={"q": "hello"})
    assert resp.status_code in (404, 500)  # index not built yet