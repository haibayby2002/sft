# data/vectorstore/embedder.py

from sentence_transformers import SentenceTransformer

class Embedder:
    """
    Page-level text embedder using SentenceTransformers.
    """
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # ✅ Recommended: small, fast, and accurate for semantic search
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text):
        """
        Generate an embedding vector for a given text.
        Returns: List[float]
        """
        if not text.strip():
            return []
        vector = self.model.encode(text, show_progress_bar=False, normalize_embeddings=True)
        return vector.tolist()
