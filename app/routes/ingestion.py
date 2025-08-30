from fastapi import APIRouter, UploadFile
import shutil, os
import sqlite3
from app.db import DB_NAME
from app.services.pdf_parser import extract_text_from_pdf
from app.services.chunker import chunk_text

router = APIRouter()

UPLOAD_DIR = "data/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    filetype = "pdf" if file.filename.endswith(".pdf") else "txt"

    # Extract text
    if filetype == "pdf":
        text = extract_text_from_pdf(filepath)
    else:
        text = open(filepath, "r", encoding="utf-8").read()

    # Chunk text
    chunks = chunk_text(text)

    # Store metadata + chunks in DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (filename, filetype, filepath) VALUES (?, ?, ?)", 
                   (file.filename, filetype, filepath))
    file_id = cursor.lastrowid

    for idx, chunk in enumerate(chunks):
        cursor.execute("INSERT INTO chunks (file_id, chunk_index, content) VALUES (?, ?, ?)", 
                       (file_id, idx, chunk))

    conn.commit()
    conn.close()

    return {"file_id": file_id, "filename": file.filename, "chunks": len(chunks)}

@router.get("/list")
def list_files():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files")
    rows = cursor.fetchall()
    conn.close()
    return rows

@router.get("/download/{file_id}")
def download_file(file_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT filepath FROM files WHERE id=?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"error": "File not found"}
    filepath = row[0]
    return {"filepath": filepath}