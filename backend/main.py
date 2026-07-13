# backend/main.py
#
# FastAPI backend — FAQ-based RAG.
#
# Changes from Phase 3 original:
#   1. Imports ask_llm_with_rag instead of ask_llm.
#   2. AskResponse includes a `sources` field (which FAQ sections were used).
#   3. /ask endpoint runs retrieval before calling the LLM.
#   4. /health now reports whether the FAQ file is loaded.
#
# No startup index-building is needed — the FAQ is parsed on every request
# (it's a small text file, so this takes < 1 ms).

import logging
import sys
import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))

from llm_client import ask_llm_with_rag, find_relevant_faq
from config import APP_NAME, APP_VERSION, LOG_FILE

# Path to the FAQ file — sits next to main.py in the backend/ folder
FAQ_PATH = os.path.join(os.path.dirname(__file__), "faq.txt")

# ── Logging ────────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── FastAPI App ────────────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_NAME,
    description="Self-hosted LLM student support assistant with FAQ-based RAG.",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import documents
app.include_router(documents.router)

# ── Data models ────────────────────────────────────────────────────────────────

from typing import Optional

class AskRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class AskResponse(BaseModel):
    question:  str
    answer:    str
    timestamp: str
    sources:   list[str] = []  # FAQ section names used to generate the answer

class HealthResponse(BaseModel):
    status:      str
    service:     str
    version:     str
    faq_loaded:  bool


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Check if the backend is running and whether the FAQ file is present."""
    faq_present = os.path.exists(FAQ_PATH)
    logger.info(f"Health check — FAQ loaded: {faq_present}")
    return HealthResponse(
        status="ok",
        service=APP_NAME,
        version=APP_VERSION,
        faq_loaded=faq_present,
    )


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    """
    Receive a student question, retrieve relevant FAQ sections,
    inject them into the LLM prompt, and return the answer.
    """
    question = request.question.strip()

    # Input validation
    if not question:
        logger.warning("Empty question received")
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if len(question) > 1000:
        logger.warning("Question too long")
        raise HTTPException(status_code=400, detail="Question is too long (max 1000 characters).")

    logger.info(f"Question: {question}")

    try:
        # Step 1 — retrieve context from ChromaDB
        from backend.services.retriever import retrieve_context
        from backend.llm_client import ask_llm_with_rag
        
        context, sections_used = retrieve_context(question, request.session_id)
        if sections_used:
            logger.info(f"Retrieved context from sources: {sections_used}")
        else:
            logger.info("No context met the relevance threshold — using model knowledge")

        # Step 2 — generate the answer
        answer = ask_llm_with_rag(question, context)
        timestamp = datetime.now().isoformat()

        logger.info(f"Answer generated ({len(answer)} chars)")

        return AskResponse(
            question=question,
            answer=answer,
            timestamp=timestamp,
            sources=sections_used,
        )

    except ConnectionError as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(status_code=503, detail="The AI model is not running. Start Ollama.")

    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        raise HTTPException(status_code=504, detail="The model timed out. Please try again.")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")