from backend.services.session_manager import create_session_collection, delete_session_collection
from backend.database import get_chroma_client
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_delete_session_logic():
    # 1. Create a dummy session
    session_id = create_session_collection("Test cleanup text.")
    chroma = get_chroma_client()
    
    # 2. Assert it exists
    collection = chroma.get_collection(f"temp_{session_id}")
    assert collection.count() > 0
    
    # 3. Call delete
    delete_session_collection(session_id)
    
    # 4. Assert it is gone
    try:
        chroma.get_collection(f"temp_{session_id}")
        assert False, "Collection should have been deleted"
    except Exception:
        assert True

def test_delete_endpoint():
    # 1. Create dummy session directly
    session_id = create_session_collection("Test API cleanup text.")
    
    # 2. Call the endpoint
    response = client.delete(f"/api/session/{session_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # 3. Verify in db
    chroma = get_chroma_client()
    try:
        chroma.get_collection(f"temp_{session_id}")
        assert False, "Collection should have been deleted"
    except Exception:
        assert True
