# Student Support LLM Assistant

A production-grade, self-hosted Large Language Model (LLM) application designed to assist university students. Built with a FastAPI backend, a React/Vite frontend, and locally served LLMs via Ollama, this project demonstrates a complete AI deployment pipeline.

## Key Features

*   **Local LLM Serving:** Fully private and offline AI inference using Ollama (e.g., `llama3.2:1b`).
*   **Retrieval-Augmented Generation (RAG):** 
    *   *Base Knowledge:* Ingests university policies and FAQs into a local ChromaDB vector store.
    *   *In-Chat File Uploads:* Users can upload `.txt`, `.md`, `.pdf`, or `.docx` files directly in the chat to ask questions against specific documents dynamically.
*   **Production Authentication:** Secured via a global Access Code (`X-Access-Token`), preventing unauthorized access to the LLM backend.
*   **Response Evaluation:** Built-in telemetry allowing users to rate responses (Good/Average/Poor), logging telemetry data for continuous model improvement.
*   **Dockerized Deployment:** Fully containerized architecture using Docker Compose for seamless deployment anywhere.

## System Architecture

*   **Frontend:** React + Vite, styled with custom CSS and Lucide-React icons.
*   **Backend:** FastAPI, providing high-performance async endpoints.
*   **Vector Database:** ChromaDB, handling dynamic document embeddings and session-based retrieval.
*   **AI Engine:** Ollama, running open-weights models locally.

## Setup Instructions

### Option 1: Docker (Recommended)
Ensure Docker and Ollama are installed on your host machine.

1. Create a `.env` file in the root directory (copy from `.env.example`).
2. Set your `SECRET_ACCESS_CODE` in the `.env` file.
3. Start the system:
   ```bash
   docker compose up -d --build
   ```
4. Access the frontend at `http://localhost:5173`.

### Option 2: Local Development
1. Start Ollama: `ollama serve` (ensure your model is pulled).
2. Start the Backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r ../requirements.txt
   uvicorn main:app --reload --port 8000
   ```
3. Start the Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Authentication
The system requires an Access Code to function. Upon opening the web app, you will be prompted to enter the `SECRET_ACCESS_CODE` defined in your `.env` file (default: `udsm2026`).

## Evaluation Data
User feedback is automatically recorded in `backend/data/feedback.csv`, tracking timestamps, user queries, LLM responses, and the corresponding rating.
