import requests
from typing import List
from backend.config import OLLAMA_BASE_URL, EMBEDDING_MODEL_NAME

OLLAMA_API_URL = f"{OLLAMA_BASE_URL}/api/embeddings"

def generate_embedding(text: str) -> List[float]:
    payload = {
        "model": EMBEDDING_MODEL_NAME,
        "prompt": text
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to generate embedding: {response.text}")
    return response.json().get("embedding", [])
