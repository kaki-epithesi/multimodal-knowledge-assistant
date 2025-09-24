# Changelog

## v0.5 – Summarizer Integration in QA
**Release Date:** 25-09-2025  

### ✨ Features
- Integrated **summarization** directly into the `/query` endpoint:
  - After retrieving top-k chunks, system now synthesizes an **answer** field.
  - Default summarizer: **TextRank** (fast extractive).
  - Optional summarizer: **Transformer** (abstractive, e.g. `facebook/bart-large-cnn`).
- Updated `QueryResponse` model to include an `answer` field.
- New `summarizer.py` service provides unified summarization interface.
- Fallback mechanism: if transformer fails, falls back to TextRank.

### 🧪 Testing
- Updated `tests/test_qa.py` to assert presence of `answer` in response.
- Transformer summarizer tests skipped in CI (heavy dependency).

### 📦 Dependencies
- Added `sumy` for TextRank.
- Added `transformers` (with `torch`) for abstractive summarization.

---

## v0.4 – Hybrid Retrieval (BM25 + Semantic with FAISS)
**Release Date:** 11-09-2025  

### ✨ Features
- Introduced **hybrid retrieval** pipeline:
  - Integrated **Sentence-Transformers** for generating semantic embeddings.
  - Added **FAISS** vector index for efficient similarity search.
  - Fused semantic (FAISS) and lexical (BM25) scores via min-max normalization and weighted combination.
- Extended `Indexer` service:
  - New `method="hybrid"` mode builds both BM25 and FAISS indexes.
  - Persists FAISS index to `data/faiss.index` and metadata to `data/index.pkl`.
- Extended `Retriever` service:
  - Loads hybrid index and performs combined retrieval.
  - Returns fused ranked snippets with both semantic and BM25 signals.
- Updated ingestion flow:
  - After file upload and chunking, all chunks in SQLite can now be indexed using hybrid mode.
- Improved `/query` endpoint:
  - Returns 404 if index not built.
  - Supports hybrid retrieval results in addition to BM25/TF-IDF.

### 🧪 Testing
- Updated `tests/test_qa.py`:
  - Mocked retriever for CI to avoid heavy FAISS/transformer dependencies.
  - Fixed test assertions to validate JSON response shape instead of tuple unpacking.
- Existing ingestion and health tests remain valid.

### 📦 Dependencies
- Added `sentence-transformers` for embeddings.
- Added `faiss-cpu` (or `faiss-gpu` if using GPU) for vector indexing.
- Retained `rank-bm25` and `scikit-learn` for lexical retrieval.

---

## v0.3 – Basic Q&A (BM25/TF-IDF Retrieval)
**Release Date:** 01-09-2025  

### ✨ Features
- Added **Q&A retrieval pipeline** using BM25/TF-IDF:
  - Implemented `Indexer` service to build and persist retrieval index (`data/index.pkl`).
  - Implemented `Retriever` service to load index and fetch top-k ranked snippets.
  - Added `POST /query` endpoint to retrieve relevant text snippets from ingested documents.
- Updated ingestion flow:
  - After file upload and chunking, all chunks in SQLite are used to rebuild the BM25 index.
  - Ensures queries are available immediately after document ingestion.
- Supports multiple document ingestion (all chunks across files are included in index).

### 🧪 Testing
- Added `tests/test_qa.py` for query endpoint:
  - Returns 404 if index not built.
  - Returns ranked snippets when index exists.
- Ingestion tests still valid and extended to check indexing flow.

### 📦 Dependencies
- Added `rank-bm25` and `scikit-learn` for BM25 and TF-IDF retrieval.
- Reused existing dependencies (`fastapi`, `uvicorn`, `pymupdf`, `pytest`, `httpx`, `python-multipart`).

---

## v0.2 – Ingestion (PDF/TXT)
**Release Date:** 30-08-2025  

### ✨ Features
- Added ingestion endpoints in FastAPI:
  - `POST /ingestion/upload` → Upload PDF/TXT files.
  - `GET /ingestion/list` → List uploaded files with metadata.
  - `GET /ingestion/download/{file_id}` → Download stored file by ID.
- Integrated **PyMuPDF** (`fitz`) for PDF text extraction.  
- Implemented simple text chunking (~500 words per chunk).  
- Implemented **SQLite storage** for file metadata and text chunks.  

### 🧪 Testing
- Added pytest tests for ingestion:
  - TXT file upload and chunk storage.  
  - PDF file upload and text extraction.  
  - File listing.  
  - File download by ID.  
- DB reset before each test to ensure isolation.  

### 📦 Dependencies
- Added `fastapi`, `uvicorn`, `pymupdf`, `pytest`, `httpx`, `python-multipart` to `requirements.txt`.  

### 🔧 CI
- CI updated to install dependencies and run `pytest -v`.  

---

## v0.1 – Project Setup  
**Release Date:** 29-08-2025  

### ✨ Features
- Initial FastAPI project structure with health check endpoint.  
- Added CI pipeline with pytest for automated testing.  
- Added basic `requirements.txt` and `changelog.md`.  