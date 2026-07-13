import os
import chromadb

# Determine the absolute path for the chroma database directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

def get_chroma_client() -> chromadb.PersistentClient:
    """
    Initializes and returns a persistent ChromaDB client.
    Creates the database directory if it does not exist.
    """
    if not os.path.exists(CHROMA_DB_DIR):
        os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    
    # Initialize the PersistentClient
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    return client
