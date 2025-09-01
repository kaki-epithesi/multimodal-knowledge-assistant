# Changelog

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