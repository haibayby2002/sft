# data/vectorstore/vector_db.py

import faiss
import numpy as np
import os
import json

VEC_STORE_PATH = "data/vectorstore/index.faiss"
META_STORE_PATH = "data/vectorstore/metadata.json"

class VectorDB:
    """
    FAISS index for embeddings + JSON metadata store.
    Stores (embedding, content_text, metadata) for page-level search.
    """

    def __init__(self, dim=384):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)  # cosine similarity
        self.entries = []  # store list of {"content": str, "metadata": dict}

        self._load()

    def _load(self):
        if os.path.exists(VEC_STORE_PATH):
            self.index = faiss.read_index(VEC_STORE_PATH)
        if os.path.exists(META_STORE_PATH):
            with open(META_STORE_PATH, "r", encoding="utf-8") as f:
                self.entries = json.load(f)

    def _save(self):
        faiss.write_index(self.index, VEC_STORE_PATH)
        with open(META_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

    def add_vector(self, vector, content_text, metadata):
        """
        Add embedding with text and metadata.
        """
        if vector is None:
            return
        np_vec = np.array([vector], dtype="float32")
        self.index.add(np_vec)
        self.entries.append({
            "content": content_text,
            "metadata": metadata
        })
        self._save()

    def search_vectors(self, query_vector, top_k=5):
        """
        Search for most similar vectors by cosine similarity.
        Returns: List[{"score": float, "content": str, "metadata": dict}]
        """
        if not self.entries:
            return []

        np_q = np.array([query_vector], dtype="float32")
        scores, ids = self.index.search(np_q, top_k)

        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0 or idx >= len(self.entries):
                continue
            entry = self.entries[idx]
            results.append({
                "score": float(score),
                "content": entry["content"],
                "metadata": entry["metadata"]
            })
        return results

    def clear(self):
        """
        Clear all vectors and metadata.
        """
        self.index = faiss.IndexFlatIP(self.dim)
        self.entries = []
        self._save()
