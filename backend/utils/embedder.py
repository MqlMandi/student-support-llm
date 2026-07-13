import requests
from typing import List

OLLAMA_API_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "nomic-embed-text:latest"

def generate_embedding(text: str) -> List[float]:
    payload = {
        "model": MODEL_NAME,
        "prompt": text
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to generate embedding: {response.text}")
    return response.json().get("embedding", [])
