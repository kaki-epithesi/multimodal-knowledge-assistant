# Changelog

## v0.2 – Ingestion (PDF/TXT)
**Release Date:** 2025-08-30  

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


## v0.1 – Project Setup  
**Release Date:** 2025-08-29  

### ✨ Features
- Initial FastAPI project structure with health check endpoint.  
- Added CI pipeline with pytest for automated testing.  
- Added basic `requirements.txt` and `changelog.md`.  