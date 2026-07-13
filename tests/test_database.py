import os
import requests
from backend.database import get_chroma_client, CHROMA_DB_DIR

def test_get_chroma_client():
    # Attempt to get the client
    client = get_chroma_client()
    
    # Check that the directory was created
    assert os.path.exists(CHROMA_DB_DIR), "ChromaDB directory was not created."
    
    # Check that the client is valid by calling a simple method like heartbeat
    assert client.heartbeat() is not None, "Client did not return a valid heartbeat."

def test_ollama_reachable():
    # Validate that Ollama is reachable at localhost:11434
    try:
        response = requests.get("http://localhost:11434/")
        assert response.status_code == 200, "Ollama is reachable but returned non-200 status."
    except requests.exceptions.ConnectionError:
        assert False, "Ollama is not reachable at http://localhost:11434. Please ensure it is running."
