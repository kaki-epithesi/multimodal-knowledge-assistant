import os
import pickle
from typing import List, Tuple, Optional

INDEX_FILE = "data/index.pkl"
FAISS_INDEX_FILE = "data/faiss.index"

# lightweight optional imports for hybrid mode
try:
    from rank_bm25 import BM25Okapi
except Exception:
    BM25Okapi = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except Exception:
    TfidfVectorizer = None

# optional heavy deps for hybrid (import inside functions to avoid import-time failures)
# sentence-transformers and faiss are only required if you choose method="hybrid"


class Indexer:
    """
    Backwards-compatible Indexer.

    Supported methods:
      - "bm25"   : uses rank_bm25 (documents = list[str])
      - "tfidf"  : uses sklearn TfidfVectorizer (documents = list[str])
      - "hybrid" : BM25 + SentenceTransformer embeddings + FAISS index (documents = list[str])
                   This will create a separate faiss index file (data/faiss.index)
    """

    def __init__(self, method: str = "bm25"):
        self.method = method
        self.index = None
        self.documents: List[str] = []
        self.vectorizer = None
        # for hybrid:
        self.faiss_index_path = FAISS_INDEX_FILE

    def build_index(self, chunks: List[str]):
        """
        Build index from text chunks (list of strings).
        This preserves your previous interface: pass a list[str] (chunks).
        """
        self.documents = chunks

        os.makedirs("data", exist_ok=True)

        if self.method == "bm25":
            if BM25Okapi is None:
                raise RuntimeError("rank_bm25 is not installed. Install it to use bm25.")
            tokenized = [doc.split() for doc in chunks]
            self.index = BM25Okapi(tokenized)

        elif self.method == "tfidf":
            if TfidfVectorizer is None:
                raise RuntimeError("scikit-learn is not installed or TfidfVectorizer unavailable.")
            self.vectorizer = TfidfVectorizer()
            self.index = self.vectorizer.fit_transform(chunks)

        elif self.method == "hybrid":
            # Hybrid: BM25 + FAISS (sentence-transformers)
            # Import heavy libs here to avoid import-time errors for non-hybrid use
            try:
                from rank_bm25 import BM25Okapi as _BM25
            except Exception as e:
                raise RuntimeError("rank_bm25 is required for hybrid mode.") from e

            try:
                from sentence_transformers import SentenceTransformer
            except Exception as e:
                raise RuntimeError("sentence-transformers is required for hybrid mode.") from e

            try:
                import faiss
                import numpy as np
            except Exception as e:
                raise RuntimeError("faiss (faiss-cpu or faiss-gpu) is required for hybrid mode.") from e

            # build BM25
            tokenized = [doc.split() for doc in chunks]
            self.index = _BM25(tokenized)  # reuse self.index to store bm25 object

            # build sentence-transfomer embeddings -> FAISS index
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            model = SentenceTransformer(model_name)
            # encode texts in batches (SentenceTransformer handles batching)
            embeddings = model.encode(chunks, show_progress_bar=False, convert_to_numpy=True, dtype="float32")
            # normalize for cosine with inner-product
            faiss.normalize_L2(embeddings)
            d = embeddings.shape[1]
            faiss_index = faiss.IndexFlatIP(d)  # inner product on normalized vectors == cosine
            faiss_index.add(embeddings)
            # persist faiss index
            faiss.write_index(faiss_index, self.faiss_index_path)

        else:
            raise ValueError("Unsupported method: choose 'bm25', 'tfidf', or 'hybrid'")

        # save metadata and index (pickle). For hybrid, index holds BM25 instance; faiss saved separately.
        with open(INDEX_FILE, "wb") as f:
            pickle.dump({
                "method": self.method,
                "documents": self.documents,
                # do not attempt to pickle faiss index here (we saved separately),
                "index": self.index,
                "vectorizer": getattr(self, "vectorizer", None),
                "faiss_index_path": self.faiss_index_path if self.method == "hybrid" else None,
            }, f)

    def _save(self):
        """Backward-compatible saver (kept for compatibility; build_index already saves)."""
        with open(INDEX_FILE, "wb") as f:
            pickle.dump({
                "method": self.method,
                "documents": self.documents,
                "index": self.index,
                "vectorizer": getattr(self, "vectorizer", None),
                "faiss_index_path": self.faiss_index_path if self.method == "hybrid" else None,
            }, f)

    def add(self, new_chunks: List[str]):
        """
        Simple append + rebuild strategy:
        - Append new_chunks to self.documents and rebuild index from combined corpus.
        This is safe and simple for v0.4. For large corpora, implement incremental addition.
        """
        combined = (self.documents or []) + new_chunks
        self.build_index(combined)