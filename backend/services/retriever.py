from typing import Optional, List
from backend.database import get_chroma_client
from backend.utils.embedder import generate_embedding
import logging

logger = logging.getLogger(__name__)

def retrieve_context(question: str, session_id: Optional[str] = None, k: int = 3) -> tuple[str, List[str]]:
    """
    Retrieves the top_k most relevant chunks from ChromaDB.
    Queries the session collection if session_id is provided,
    otherwise queries the global university_faq collection.
    
    Returns a tuple of (context_string, list_of_sources).
    """
    client = get_chroma_client()
    
    if session_id:
        collection_name = f"temp_{session_id}"
        logger.info(f"Querying temporary collection: {collection_name}")
    else:
        collection_name = "university_faq"
        logger.info("Querying global university_faq collection")
        
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        logger.warning(f"Collection {collection_name} not found. Returning empty context.")
        return "", []
        
    # Generate embedding for the question
    question_embedding = generate_embedding(question)
    
    # Query ChromaDB
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=k
    )
    
    if not results or not results['documents'] or not results['documents'][0]:
        return "", []
        
    documents = results['documents'][0]
    metadatas = results['metadatas'][0] if results.get('metadatas') and results['metadatas'][0] else []
    
    # Format the retrieved documents into a single context string
    context_blocks = []
    sources = []
    
    for i, doc in enumerate(documents):
        source_name = "Unknown Source"
        if i < len(metadatas) and metadatas[i]:
            source_name = metadatas[i].get("source", metadatas[i].get("session_id", "Uploaded Document"))
            
        if source_name not in sources:
            sources.append(source_name)
            
        context_blocks.append(f"[Source: {source_name}]\n{doc}")
        
    return "\n\n---\n\n".join(context_blocks), sources
