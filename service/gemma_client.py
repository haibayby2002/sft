import requests
import json

def query_gemma(prompt: str, context: str = None) -> str:
    """
    Query Gemma LLM with optional context. Returns a full response.
    """
    if context:
        prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}"

    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "gemma3n:e2b",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.RequestException as e:
        return f"[Error] Failed to query Gemma: {str(e)}"


def query_gemma_stream(prompt: str, context: str = None):
    """
    Stream response from local Ollama Gemma model with optional context and yield chunks of response text.
    """
    # print(context)
    if context:
        prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}"

    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "gemma3n:e2b",
        "prompt": prompt,
        "stream": True
    }

    try:
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=120) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    data = json.loads(line.strip())
                    chunk = data.get("response")
                    if chunk:
                        yield chunk
                    if data.get("done"):
                        break
                except json.JSONDecodeError as e:
                    yield f"\n[Error parsing stream chunk: {e}]\n"
    except requests.RequestException as e:
        yield f"[Error] Streaming failed: {str(e)}"
