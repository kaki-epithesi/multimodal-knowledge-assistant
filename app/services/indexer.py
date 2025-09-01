import os
import pickle
from typing import List

from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer


INDEX_FILE = "data/index.pkl"


class Indexer:
    def __init__(self, method: str = "bm25"):
        self.method = method
        self.index = None
        self.documents = []

    def build_index(self, chunks: List[str]):
        """Builds index from text chunks."""
        self.documents = chunks

        if self.method == "bm25":
            tokenized = [doc.split() for doc in chunks]
            self.index = BM25Okapi(tokenized)
        elif self.method == "tfidf":
            self.vectorizer = TfidfVectorizer()
            self.index = self.vectorizer.fit_transform(chunks)
        else:
            raise ValueError("Unsupported method: choose 'bm25' or 'tfidf'")

        self._save()

    def _save(self):
        os.makedirs("data", exist_ok=True)
        with open(INDEX_FILE, "wb") as f:
            pickle.dump({
                "method": self.method,
                "documents": self.documents,
                "index": self.index,
                "vectorizer": getattr(self, "vectorizer", None)
            }, f)