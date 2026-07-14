import os
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from backend.utils.auth import verify_token
from backend.services.session_manager import create_session_collection
from backend.utils.document_parser import parse_file

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/upload", dependencies=[Depends(verify_token)])
async def upload_temp_document(file: UploadFile = File(...)):
    allowed_extensions = (".txt", ".md", ".pdf", ".docx")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail=f"Only {', '.join(allowed_extensions)} files are supported.")
        
    temp_file_path = None
    try:
        # Create a temporary file to save the upload stream
        fd, temp_file_path = tempfile.mkstemp(suffix=os.path.splitext(file.filename)[1].lower())
        with os.fdopen(fd, 'wb') as f:
            f.write(await file.read())
            
        # Parse the file using the robust parser
        text = parse_file(temp_file_path)
        
        # Ingest into ChromaDB
        session_id = create_session_collection(text)
        
        logger.info(f"Created temporary session {session_id} for uploaded file {file.filename}")
        
        return {"session_id": session_id, "filename": file.filename}
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file from the hard drive
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.delete("/api/session/{session_id}", dependencies=[Depends(verify_token)])
def end_session(session_id: str):
    try:
        from backend.services.session_manager import delete_session_collection
        delete_session_collection(session_id)
        logger.info(f"Deleted temporary session {session_id}")
        return {"status": "success", "message": f"Session {session_id} deleted."}
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
