import os
import io
import sqlite3
import fitz  # PyMuPDF
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import DB_NAME, init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Fresh DB for each test
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    init_db()
    yield
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)


def test_upload_txt():
    content = b"Hello world. This is a test file."
    response = client.post(
        "/ingestion/upload",
        files={"file": ("test.txt", content, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["chunks"] >= 1


def test_upload_pdf():
    # Create a minimal PDF in-memory
    pdf_buffer = io.BytesIO()
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello PDF World")
    doc.save(pdf_buffer)
    doc.close()
    pdf_buffer.seek(0)

    response = client.post(
        "/ingestion/upload",
        files={"file": ("test.pdf", pdf_buffer, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["chunks"] >= 1


def test_list_files():
    # Upload one file first
    client.post(
        "/ingestion/upload",
        files={"file": ("sample.txt", b"some text here", "text/plain")},
    )
    response = client.get("/ingestion/list")
    assert response.status_code == 200
    files = response.json()
    assert len(files) >= 1
    assert files[0][1] == "sample.txt"  # filename


def test_download_file():
    # Upload a file first
    upload_resp = client.post(
        "/ingestion/upload",
        files={"file": ("download.txt", b"download me", "text/plain")},
    )
    file_id = upload_resp.json()["file_id"]

    response = client.get(f"/ingestion/download/{file_id}")
    assert response.status_code == 200
    data = response.json()
    assert "filepath" in data
    assert os.path.exists(data["filepath"])