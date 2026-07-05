# tests/test_api.py
# Run with: python tests/test_api.py
# (Make sure the backend is running first)

import httpx

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Backend should return status: ok."""
    response = httpx.get(f"{BASE_URL}/health", timeout=10.0)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "ok", "Status should be 'ok'"
    print("✅ Test 1 PASSED: Health check")

def test_ask_valid_question():
    """A valid question should return a 200 response with an answer."""
    response = httpx.post(
        f"{BASE_URL}/ask",
        json={"question": "How do I register for a course?"},
        timeout=90.0          # LLM responses can take a while
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "answer" in data, "Response should have an 'answer' field"
    assert "question" in data, "Response should echo back the 'question'"
    assert "timestamp" in data, "Response should have a 'timestamp'"
    assert len(data["answer"]) > 0, "Answer should not be empty"
    print(f"✅ Test 2 PASSED: Valid question answered")
    print(f"   Preview: {data['answer'][:80]}...")

def test_ask_empty_question():
    """An empty question should return a 400 Bad Request error."""
    response = httpx.post(
        f"{BASE_URL}/ask",
        json={"question": ""},
        timeout=10.0
    )
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    print("✅ Test 3 PASSED: Empty question correctly rejected")

def test_ask_whitespace_question():
    """A whitespace-only question should also be rejected."""
    response = httpx.post(
        f"{BASE_URL}/ask",
        json={"question": "   "},
        timeout=10.0
    )
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    print("✅ Test 4 PASSED: Whitespace question correctly rejected")

def test_ask_library_question():
    """Test a second valid question about a different topic."""
    response = httpx.post(
        f"{BASE_URL}/ask",
        json={"question": "What are the library opening hours?"},
        timeout=90.0
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert len(data["answer"]) > 0
    print(f"✅ Test 5 PASSED: Library question answered")
    print(f"   Preview: {data['answer'][:80]}...")

if __name__ == "__main__":
    print("=" * 50)
    print("Running API Tests — University Student Support")
    print("=" * 50)
    print()

    tests = [
        test_health_check,
        test_ask_valid_question,
        test_ask_empty_question,
        test_ask_whitespace_question,
        test_ask_library_question,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {test.__name__} — {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {test.__name__} — {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("✅ All tests passed!")
    print("=" * 50)