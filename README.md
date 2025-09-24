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
│  │  └─ qa.py               # Query API (retrieval + summarizer)
│  └─ services/
│     ├─ pdf_parser.py       # PyMuPDF text extraction
│     ├─ chunker.py          # Text chunking
│     ├─ indexer.py          # Index builder (BM25 / TF-IDF / Hybrid with FAISS)
│     ├─ retriever.py        # Query retriever
│     └─ summarizer.py       # TextRank + Transformer summarizers
├─ data/                     # Uploaded files + serialized index (ignored in Git)
├─ tests/
│  ├─ test_ingestion.py      # Pytest for ingestion
│  ├─ test_health.py         # Pytest for health
│  └─ test_qa.py             # Pytest for QA flow
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
    - Body: form-data → key=file (File type) → choose PDF or TXT
    - Process:
	  - Saves file to /data
	  -	Extracts text (pdf_parser.py for PDFs, raw read for TXT)
	  -	Splits into chunks (chunker.py)
	  -	Stores into SQLite (files and chunks tables)
	  -	Rebuilds index (BM25 by default, hybrid optional)
  - Example Response
    ```json
    {
      "file_id": 1,
      "filename": "example.pdf",
      "chunks": 12,
      "status": "ingested + indexed"
    }
    ```
- GET /ingestion/list → List uploaded files with metadata.
- GET /ingestion/download/{file_id} → Download file by ID.

### Query
- POST /query → Query ingested documents and return top-k ranked snippets.

#### Example:
```json
{
  "q": "What is hybrid retrieval?",
  "top_k": 3
}
```
#### Example Response:
```json
{
  "query": "What is hybrid retrieval?",
  "results": [
    {"text": "Hybrid retrieval combines BM25 and vector embeddings.", "score": 0.95},
    {"text": "It improves ranking via semantic similarity and keyword overlap.", "score": 0.87}
  ],
  "answer": "Hybrid retrieval is a method that fuses BM25 with vector embeddings to improve relevance ranking."
}
```
## 🛠️ Implementation Notes

- FastAPI + Uvicorn → REST API server
- SQLite → file metadata & chunk storage
- PyMuPDF (fitz) → PDF text extraction
- rank-bm25 → BM25 retrieval
- scikit-learn → TF-IDF retrieval
- sentence-transformers + faiss-cpu → semantic vector search (hybrid mode)
- sumy → TextRank summarizer
- transformers → optional abstractive summarization (e.g. facebook/bart-large-cnn)
- pytest → test suite with retriever mocked in CI for speed/stability
-	All runtime data (/data/, DB file, FAISS index) is .gitignored


## Version History
- v0.5 → Integrated summarizer into QA endpoint (TextRank default, Transformer optional)
- v0.4 → Added hybrid retrieval (BM25 + Sentence-Transformers embeddings with FAISS); updated retriever & tests
- v0.3 → Added Q&A retrieval (BM25/TF-IDF), /query endpoint, integrated indexing into ingestion.
- v0.2 → Added ingestion of PDF/TXT with upload, list, download APIs, SQLite storage, PyMuPDF parsing, and tests.
- v0.1 → Initial FastAPI backend with /health endpoint and CI setup.

