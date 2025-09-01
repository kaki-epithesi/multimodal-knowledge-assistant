import pickle
import numpy as np
from typing import List, Tuple

from .indexer import INDEX_FILE


class Retriever:
    def __init__(self):
        with open(INDEX_FILE, "rb") as f:
            data = pickle.load(f)

        self.method = data["method"]
        self.documents = data["documents"]
        self.index = data["index"]
        self.vectorizer = data.get("vectorizer", None)

    def query(self, q: str, top_k: int = 3) -> List[Tuple[str, float]]:
        if self.method == "bm25":
            tokenized_query = q.split()
            scores = self.index.get_scores(tokenized_query)
            ranked = np.argsort(scores)[::-1][:top_k]
            return [(self.documents[i], float(scores[i])) for i in ranked]

        elif self.method == "tfidf":
            q_vec = self.vectorizer.transform([q])
            scores = (self.index @ q_vec.T).toarray().ravel()
            ranked = np.argsort(scores)[::-1][:top_k]
            return [(self.documents[i], float(scores[i])) for i in ranked]

        else:
            raise ValueError("Unknown method")