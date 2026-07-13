import uuid
from backend.database import get_chroma_client
from backend.utils.chunker import chunk_text
from backend.utils.embedder import generate_embedding

def create_session_collection(text: str) -> str:
    """
    Takes raw text, chunks it, generates embeddings,
    and stores it in an ephemeral ChromaDB collection.
    Returns the session ID (UUID).
    """
    session_id = str(uuid.uuid4())
    collection_name = f"temp_{session_id}"
    
    client = get_chroma_client()
    collection = client.create_collection(name=collection_name)
    
    chunks = chunk_text(text)
    
    ids = []
    embeddings = []
    documents = []
    
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        
        emb = generate_embedding(chunk)
        ids.append(str(uuid.uuid4()))
        embeddings.append(emb)
        documents.append(chunk)
        
    if ids:
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=[{"session_id": session_id} for _ in ids]
        )
        
    return session_id
