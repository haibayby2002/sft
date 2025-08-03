# app/query_engine.py

from data.vectorstore.embedder import Embedder
from data.vectorstore.vector_db import VectorDB
from data.vectorstore.metadata_format import format_context
from service.rag_pipeline import ask_gemma_with_context

embedder = Embedder()
vector_db = VectorDB()

def query_slides(user_question, top_k=5):
    """
    1. Embed user question
    2. Search vector DB for relevant pages
    3. Build context and ask Gemma
    """
    question_embedding = embedder.embed_text(user_question)
    results = vector_db.search_vectors(question_embedding, top_k=top_k)

    if not results:
        return "No relevant pages found.", []

    context_text = format_context(results)
    answer = ask_gemma_with_context(user_question, context_text)

    pages_info = [(r["metadata"]["slide_id"], r["metadata"]["page_number"]) for r in results]
    return answer, pages_info
