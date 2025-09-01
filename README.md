# Multimodal Knowledge Assistant

Minimal working backend to boot a FastAPI server with a health endpoint.

## Quickstart

```bash
# 1) Create & activate a virtualenv (recommended)
python3 -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/health -> `{ "status": "ok", "version": "0.1" }`

## Structure

```
multimodal-knowledge-assistant/
├─ app/
│  ├─ main.py                # FastAPI entrypoint
│  ├─ db.py                  # SQLite init & schema
│  ├─ models.py              # Pydantic models (requests/responses)
│  ├─ routes/
│  │  ├─ ingestion.py        # Upload/list/download APIs
│  │  └─ qa.py               # Query API
│  └─ services/
│     ├─ pdf_parser.py       # PyMuPDF text extraction
│     ├─ chunker.py          # Simple text chunking
│     ├─ indexer.py          # BM25/TF-IDF index builder
│     └─ retriever.py        # Query retriever
├─ data/                     # Uploaded files + serialized index (ignored in Git)
├─ tests/
│  ├─ test_ingestion.py      # Pytest for ingestion
│  └─ test_qa.py             # Pytest for Q&A
├─ .gitignore
├─ requirements.txt
├─ changelog.md
└─ pyproject.toml
```
## 📡 Endpoints

### Health
- GET /health → Health check.

### Ingestion
- POST /ingestion/upload → Upload PDF/TXT → extract, chunk, store in SQLite, update index.
- GET /ingestion/list → List uploaded files with metadata.
- GET /ingestion/download/{file_id} → Download file by ID.

### Query
- POST /query → Query ingested documents and return top-k ranked snippets.
#### Example:
```json
{
  "q": "What is the introduction about?",
  "top_k": 2
}
```

## Notes
- Uses FastAPI + Uvicorn for the API.
- Uses PyMuPDF (fitz) for PDF text extraction.
- Stores file metadata & text chunks in SQLite.
- Added pytest tests for ingestion endpoints.
- Uses BM25 (default) or TF-IDF for retrieval.
- Runtime data (ingestion.db, /data/) is ignored via .gitignore.

## Version History
- v0.3 → Added Q&A retrieval (BM25/TF-IDF), /query endpoint, integrated indexing into ingestion.
- v0.2 → Added ingestion of PDF/TXT with upload, list, download APIs, SQLite storage, PyMuPDF parsing, and tests.
- v0.1 → Initial FastAPI backend with /health endpoint and CI setup.

