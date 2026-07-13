import time
import asyncio
import logging
from backend.database import get_chroma_client

logger = logging.getLogger(__name__)

# 2 hours in seconds
TTL_SECONDS = 2 * 60 * 60

async def cleanup_stale_sessions():
    """Background task to periodically delete old temporary collections."""
    while True:
        try:
            client = get_chroma_client()
            collections = client.list_collections()
            now = time.time()
            deleted_count = 0
            
            for collection in collections:
                # In ChromaDB v0.4+, list_collections returns Collection objects
                c_name = collection.name if hasattr(collection, 'name') else collection
                if c_name.startswith("temp_"):
                    # Extract metadata depending on if it's an object or string
                    c_meta = collection.metadata if hasattr(collection, 'metadata') else {}
                    
                    # If using old chromadb, we might need to get the collection first
                    if not isinstance(c_meta, dict):
                        try:
                            col_obj = client.get_collection(c_name)
                            c_meta = col_obj.metadata or {}
                        except Exception:
                            c_meta = {}
                            
                    created_at = c_meta.get("created_at", 0)
                    
                    if (now - created_at) > TTL_SECONDS:
                        client.delete_collection(c_name)
                        deleted_count += 1
                        logger.info(f"Deleted stale session collection: {c_name}")
                        
            if deleted_count > 0:
                logger.info(f"Cleanup cycle finished. Deleted {deleted_count} stale collections.")
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            
        # Sleep for 30 minutes before running again
        await asyncio.sleep(30 * 60)
