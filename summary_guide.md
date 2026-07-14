# Implementation Summary Guide

This document provides an in-depth, technical breakdown of the major systems implemented in the Student Support LLM Assistant. It serves as a comprehensive reference for the architecture, code locations, and operational workflows of the system.

---

## 1. RAG, In-Chat Implementation, and File Ingestion

The application features a powerful Retrieval-Augmented Generation (RAG) system using ChromaDB to handle both permanent university knowledge and dynamic, user-uploaded documents.

### 1.1 Core Architecture & ChromaDB
*   **Database Location:** ChromaDB writes its persistent data to the `chroma_db/` folder in the root directory.
*   **Text Parsing:** When a file is processed, `backend/utils/document_parser.py` handles the extraction of raw text from formats like `.md`, `.pdf`, and `.docx`.
*   **Vector Ingestion:** The text is passed through chunking logic and embedded using the local `nomic-embed-text` model before being saved to collections.

### 1.2 How to Run Base Ingestion (CLI Scripts)
To ingest permanent university documents into the core `university_faq` ChromaDB collection, a dedicated ingestion script is provided.

**1. To ingest a single file:**
From the root directory, run:
```bash
PYTHONPATH=. python backend/scripts/ingest_faq.py --file "./backend/data/student_handbook.md"
```
*Expected output:*
> Processing student_handbook.md...
> Successfully ingested 31 chunks from student_handbook.md

**2. To ingest an entire folder of files:**
If you want to batch process all documents inside the data folder, run:
```bash
PYTHONPATH=. python backend/scripts/ingest_faq.py --dir "./backend/data"
```
*This will scan the folder, chunk all valid documents, and embed them permanently (e.g., resulting in "Ingestion complete. Total items in collection: 79").*

### 1.3 In-Chat UI Ingestion (Temporary Sessions)
For dynamic uploads by the user:
1.  **Action:** The user clicks the paperclip icon in the frontend UI (`frontend/src/App.jsx`) and selects a file.
2.  **Flow:** A `multipart/form-data` POST request is sent to `backend/routers/documents.py` at the `/api/upload` endpoint.
3.  **Processing:** The backend saves the file to the OS `/tmp` directory, parses it, ingests it into ChromaDB under a unique `session_id`, and instantly deletes the physical file. The frontend receives the `session_id` and attaches it to subsequent chat messages to provide context.

**B. Manual / Batch Ingestion (API Level)**
To ingest files programmatically or run batch uploads without the UI:
1.  Ensure the backend is running (`uvicorn backend.main:app --reload`).
2.  Use `curl` or Postman to hit the API directly:
    ```bash
    curl -X POST "http://localhost:8000/api/upload" \
         -H "X-Access-Token: udsm2026" \
         -H "Content-Type: multipart/form-data" \
         -F "file=@/path/to/your/document.pdf"
    ```
3.  The API will return a JSON object containing the `session_id`.

---

## 2. Authentication Mechanism (Option D)

The system is secured by a global access code, preventing unauthorized LLM inference.

### 2.1 Backend Security Implementation
*   **Configuration:** The secret is stored in the root `.env` file as `SECRET_ACCESS_CODE`. It is loaded into Python via `backend/config.py`.
*   **Auth Dependency:** The core logic lives in `backend/utils/auth.py`. We defined a FastAPI Dependency called `verify_token` that looks for the `X-Access-Token` HTTP header. If the header does not match the secret, it raises a `401 Unauthorized` exception.
*   **Endpoint Protection:** In `backend/main.py` and `backend/routers/documents.py`, this dependency is injected directly into the route definitions:
    ```python
    @app.post("/ask", response_model=AskResponse, dependencies=[Depends(verify_token)])
    ```

### 2.2 Frontend Flow
*   **State Management:** In `frontend/src/App.jsx`, React state variables `accessCode` and `isAuthenticated` govern the UI. If `isAuthenticated` is false, the main chat shell is hidden, and an absolute-positioned `.auth-overlay` is rendered instead.
*   **Persistent Login:** Upon entering the correct code, it is saved to the browser's `localStorage`.
*   **Axios Interceptor:** Once authenticated, the code is globally bound to `axios` so that every request automatically includes the token:
    ```javascript
    axios.defaults.headers.common["X-Access-Token"] = accessCode;
    ```

---

## 3. Feedback Reaction Functionality (Option E)

To evaluate LLM responses, a comprehensive telemetry logging system was built.

### 3.1 Frontend UI (`frontend/src/components/ChatMessage.jsx`)
*   If a message belongs to the `assistant`, three buttons are rendered beneath the chat bubble: Good, Average, and Poor.
*   When a user clicks a rating, an async function `handleFeedback(rating)` sends a POST request to `/api/feedback`.
*   The payload explicitly includes the original `question`, the `answer`, and the `rating`, ensuring the data has enough context to be useful for future model tuning.

### 3.2 Backend Logging (`backend/main.py`)
*   The `/api/feedback` endpoint receives the request.
*   Using Python's standard `csv` library, it opens `backend/data/feedback.csv` in append (`a`) mode.
*   If the file does not exist, the `os.makedirs` function creates the directory, and the script writes the initial CSV headers (`Timestamp, Question, Answer, Rating`) before saving the user's data.

---

## 4. Docker Containerization (Option C)

The entire application is packaged for isolated, reproducible deployment.

*   **Backend Dockerfile:** Found at `backend/Dockerfile`. It uses `python:3.10-slim`, installs from `requirements.txt`, and exposes port `8000`.
*   **Frontend Dockerfile:** Found at `frontend/Dockerfile`. It uses a multi-stage build. First, it builds the Vite React app using Node.js. Second, it serves the static `dist/` folder using Nginx on port `80`.
*   **docker-compose.yml:** Located in the root. It networks both containers together. Crucially, it uses `host.docker.internal` to allow the containerized backend to communicate with the Ollama service running on the host machine. It also maps `/app/backend/data` and `/app/chroma_db` to local volumes to ensure data persistence across container restarts.
