# backend/llm_client.py

import httpx
from config import OLLAMA_BASE_URL, MODEL_NAME

# ── System Prompt ─────────────────────────────────────────────────────────────
# This tells the model WHO it is and WHAT it should do.
# This is the "improved prompt" for Task 6.
SYSTEM_PROMPT = """You are a helpful and friendly University Student Support Assistant.
You assist students with questions about the following topics only:
- Course registration
- Examination rules and schedules
- Library services
- ICT support
- Hostel application
- Fee payment
- Academic calendar
- Student conduct and regulations

Rules:
1. Always be polite, clear, and concise.
2. Give practical, actionable advice.
3. If you do not know the answer, say so honestly and suggest the student 
   visit the relevant university office in person.
4. Do not answer questions that are not related to university services.
"""

def ask_llm(question: str) -> str:
    """
    Send a question to the local Ollama LLM and return the text response.
    Raises specific exceptions so the backend can handle errors properly.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"

    # Combine the system prompt with the student's question
    full_prompt = f"{SYSTEM_PROMPT}\n\nStudent question: {question}\n\nAssistant:"

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False          # We want the full response at once, not streamed
    }

    try:
        with httpx.Client(timeout=90.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "No response received from the model.")

    except httpx.ConnectError:
        raise ConnectionError(
            "Cannot connect to Ollama. Make sure Ollama is running "
            "(run 'ollama serve' in a terminal)."
        )

    except httpx.TimeoutException:
        raise TimeoutError(
            "The model took too long to respond. "
            "Try a shorter question or restart Ollama."
        )

    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Ollama returned an error: {e.response.status_code}")

    except Exception as e:
        raise RuntimeError(f"Unexpected LLM error: {str(e)}")