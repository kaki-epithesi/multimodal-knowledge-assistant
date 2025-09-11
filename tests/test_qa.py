# tests/test_qa.py
# This test avoids requiring faiss/sentence-transformers in CI by monkeypatching the Retriever
import json
from fastapi.testclient import TestClient
import pytest
from app.main import app

RETRIEVER_IMPORT_PATH = "app.routes.qa.Retriever"

client = TestClient(app)


class DummyRetriever:
    def __init__(self, *args, **kwargs):
        pass

    def query(self, q, top_k=3):
        # return deterministic sample matching (text, score) tuples
        return [("This is a sample passage about hybrid retrieval.", 0.95)]


@pytest.fixture(autouse=True)
def patch_retriever(monkeypatch):
    # Monkeypatch the Retriever used by the route to be DummyRetriever.
    # If your route imports Retriever under a different path, change RETRIEVER_IMPORT_PATH.
    from importlib import import_module
    module_path, class_name = RETRIEVER_IMPORT_PATH.rsplit(".", 1)
    module = import_module(module_path)
    monkeypatch.setattr(module, class_name, DummyRetriever)
    yield


def test_query_endpoint_basic():
    payload = {"q": "what is hybrid retrieval", "top_k": 1}
    resp = client.post("/query", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == payload["q"]
    results = body.get("results")
    assert isinstance(results, list)
    assert len(results) == 1
    r_text, r_score = results[0]
    assert "hybrid retrieval" in r_text


def test_query_missing_q():
    resp = client.post("/query", json={})
    assert resp.status_code in (400, 422)