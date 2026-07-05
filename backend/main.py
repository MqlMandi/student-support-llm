# backend/main.py

import logging
import sys
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Make sure Python can find our other files in the same folder
sys.path.insert(0, os.path.dirname(__file__))

from llm_client import ask_llm
from config import APP_NAME, APP_VERSION, LOG_FILE

# ── Logging Setup ─────────────────────────────────────────────────────────────
# Create the logs directory if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),   # Write to log file
        logging.StreamHandler()          # Also print to terminal
    ]
)
logger = logging.getLogger(__name__)

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_NAME,
    description="A self-hosted LLM-powered student support chatbot.",
    version=APP_VERSION
)

# CORS — This allows your React frontend (on port 5173) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Data Models ───────────────────────────────────────────────────────────────
# Pydantic models define the shape of request and response data

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    question: str
    answer: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Check if the backend is running correctly."""
    logger.info("Health check requested")
    return HealthResponse(
        status="ok",
        service=APP_NAME,
        version=APP_VERSION
    )


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    """
    Receive a student question, send it to the local LLM, and return the answer.
    """
    question = request.question.strip()

    # Validate: reject empty questions
    if not question:
        logger.warning("Empty question received")
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if len(question) > 1000:
        logger.warning("Question too long")
        raise HTTPException(status_code=400, detail="Question is too long (max 1000 characters).")

    logger.info(f"Question received: {question}")

    try:
        answer = ask_llm(question)
        timestamp = datetime.now().isoformat()

        logger.info(f"Answer generated successfully ({len(answer)} characters)")
        logger.info(f"Answer preview: {answer[:120]}...")

        return AskResponse(question=question, answer=answer, timestamp=timestamp)

    except ConnectionError as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="The AI model is not running. Please start Ollama."
        )

    except TimeoutError as e:
        logger.error(f"Timeout error: {e}")
        raise HTTPException(
            status_code=504,
            detail="The model took too long to respond. Please try again."
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred. Please try again."
        )