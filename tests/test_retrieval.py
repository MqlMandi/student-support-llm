from backend.services.retriever import retrieve_context
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_retrieval_global():
    # Ensure it doesn't crash when called without a session_id
    context, sources = retrieve_context("What are the hostel fees?")
    assert isinstance(context, str)
    assert isinstance(sources, list)

def test_ask_endpoint_schema():
    # Test that the /ask endpoint properly accepts an optional session_id
    # We only care that it doesn't fail with a 422 Validation Error
    response = client.post("/ask", json={"question": "What is the fee?"})
    assert response.status_code != 422
    
    # Test with session_id
    response_with_session = client.post("/ask", json={"question": "What is the fee?", "session_id": "dummy-session-123"})
    assert response_with_session.status_code != 422
