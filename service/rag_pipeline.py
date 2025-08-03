# service/rag_pipeline.py

from service.gemma_client import query_gemma_stream

def ask_gemma_with_context(question, context):
    """
    Combine user question and retrieved context into a single prompt
    for Gemma.
    """
    prompt = f"""You are an assistant. Use the following slides context to answer:

{context}

Question: {question}
Answer:"""

    response = ""
    for chunk in query_gemma_stream(prompt):
        response += chunk
    return response
