import os
import pickle
import numpy as np
from typing import List, Tuple

from .indexer import INDEX_FILE

# optional heavy deps will be imported only when needed (hybrid mode)
try:
    from rank_bm25 import BM25Okapi  # for type checks only
except Exception:
    BM25Okapi = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer  # type check only
except Exception:
    TfidfVectorizer = None


class Retriever:
    """
    Backwards-compatible Retriever.

    Methods:
      - query(q: str, top_k: int) -> List[Tuple[str, float]]
    """

    def __init__(self):
        if not os.path.exists(INDEX_FILE):
            raise FileNotFoundError(f"Index file not found at {INDEX_FILE}")

        with open(INDEX_FILE, "rb") as f:
            data = pickle.load(f)

        self.method = data["method"]
        self.documents: List[str] = data["documents"]
        self.index = data["index"]
        self.vectorizer = data.get("vectorizer", None)
        self.faiss_index_path = data.get("faiss_index_path", None)

        # load faiss index only if hybrid mode
        if self.method == "hybrid":
            try:
                import faiss
            except Exception as e:
                raise RuntimeError("faiss must be installed to use hybrid retrieval.") from e
            if not self.faiss_index_path or not os.path.exists(self.faiss_index_path):
                raise FileNotFoundError("FAISS index file not found for hybrid mode. Rebuild index first.")
            self._faiss = faiss.read_index(self.faiss_index_path)
            # we'll need a sentence-transformers model at query time
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as e:
                raise RuntimeError("sentence-transformers required for hybrid retrieval (query time).") from e
            self._sbert = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def query(self, q: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Returns list of (document_text, score).
        For bm25/tfidf behavior stays the same as your previous implementation.
        For hybrid: performs semantic + bm25 fusion and returns fused score.
        """
        if self.method == "bm25":
            tokenized_query = q.split()
            scores = self.index.get_scores(tokenized_query)
            ranked = np.argsort(scores)[::-1][:top_k]
            return [(self.documents[i], float(scores[i])) for i in ranked]

        elif self.method == "tfidf":
            if self.vectorizer is None:
                raise RuntimeError("Tfidf vectorizer missing in index.")
            q_vec = self.vectorizer.transform([q])
            # self.index is a matrix: docs x features
            scores = (self.index @ q_vec.T).toarray().ravel()
            ranked = np.argsort(scores)[::-1][:top_k]
            return [(self.documents[i], float(scores[i])) for i in ranked]

        elif self.method == "hybrid":
            # semantic (FAISS) + lexical (BM25) fusion
            faiss_index = getattr(self, "_faiss", None)
            if faiss_index is None:
                raise RuntimeError("FAISS index not loaded for hybrid mode.")
            # embed query
            q_emb = self._sbert.encode([q], convert_to_numpy=True, dtype="float32")
            import faiss  # local import for faiss module (assigns 'faiss', not 'np')
            faiss.normalize_L2(q_emb)
            D, I = faiss_index.search(q_emb, top_k)  # top_k semantic candidates
            sem_idxs = I[0].tolist()
            sem_scores = D[0].tolist()  # inner-product on normalized vectors -> cosine

            # BM25 scores for all docs (fast)
            tokenized_query = q.split()
            bm25_scores = self.index.get_scores(tokenized_query)  # array of scores

            # Combine candidate set (union of top_k semantics + top_k BM25 highest)
            top_bm25_idxs = np.argsort(bm25_scores)[::-1][:top_k].tolist()
            candidate_idxs = list(dict.fromkeys(sem_idxs + top_bm25_idxs))  # preserve order, unique

            # build score arrays aligned with candidate_idxs
            sem_map = {i: 0.0 for i in candidate_idxs}
            for i, s in zip(sem_idxs, sem_scores):
                sem_map[i] = float(s)

            lex_map = {i: float(bm25_scores[i]) for i in candidate_idxs}

            # min-max normalize both lists
            sem_arr = np.array([sem_map[i] for i in candidate_idxs], dtype="float32")
            lex_arr = np.array([lex_map[i] for i in candidate_idxs], dtype="float32")

            def min_max(x):
                if x.size == 0:
                    return x
                minv = float(x.min())
                maxv = float(x.max())
                if maxv - minv < 1e-9:
                    return np.ones_like(x)
                return (x - minv) / (maxv - minv)

            sem_norm = min_max(sem_arr)
            lex_norm = min_max(lex_arr)

            # fusion weight: default equal weight (0.5 each) — you can change easily later
            alpha = 0.6
            fused = []
            for idx, s_sem, s_lex in zip(candidate_idxs, sem_norm, lex_norm):
                fused_score = float(alpha * float(s_sem) + (1 - alpha) * float(s_lex))
                fused.append((self.documents[idx], fused_score))

            # sort by fused score
            fused_sorted = sorted(fused, key=lambda x: x[1], reverse=True)[:top_k]
            return fused_sorted

        else:
            raise ValueError("Unknown method")