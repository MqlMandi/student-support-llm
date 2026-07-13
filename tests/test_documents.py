import io
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_chroma_client

client = TestClient(app)

def test_upload_endpoint_returns_uuid():
    # Simulate a file upload
    file_content = b"This is a test document for temporary upload. It contains some very useful knowledge for the AI."
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    
    response = client.post("/api/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["filename"] == "test.txt"
    
    session_id = data["session_id"]
    
    # Check isolation and existence
    chroma = get_chroma_client()
    collection = chroma.get_collection(f"temp_{session_id}")
    assert collection.count() > 0
