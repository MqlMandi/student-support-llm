import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.session_manager import create_session_collection

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/upload")
async def upload_temp_document(file: UploadFile = File(...)):
    if not file.filename.endswith((".txt", ".md")):
        raise HTTPException(status_code=400, detail="Only .txt and .md files are supported.")
        
    try:
        content = await file.read()
        text = content.decode("utf-8")
        
        session_id = create_session_collection(text)
        
        logger.info(f"Created temporary session {session_id} for uploaded file {file.filename}")
        
        return {"session_id": session_id, "filename": file.filename}
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/session/{session_id}")
def end_session(session_id: str):
    try:
        from backend.services.session_manager import delete_session_collection
        delete_session_collection(session_id)
        logger.info(f"Deleted temporary session {session_id}")
        return {"status": "success", "message": f"Session {session_id} deleted."}
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
