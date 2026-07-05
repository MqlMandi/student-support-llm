# Student Support LLM Assistant

An AI-powered student support chatbot built with a self-hosted local LLM.

Built for IS 365 — AI, UDSM

## System Requirements
- Python 3.10 or higher
- Node.js 18 or higher
- Ollama (https://ollama.com)
- 2GB free disk space

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/student-support-llm.git
cd student-support-llm
```

### Step 2: Set Up Python Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Step 3: Install and Start Ollama
1. Download Ollama from https://ollama.com
2. Pull the model:
```bash
ollama pull llama3.2:1b
ollama serve
```

### Step 4: Start the Backend (new terminal)
```bash
cd backend
uvicorn main:app --reload --port 8000
```
Backend will be available at: http://localhost:8000
API docs available at: http://localhost:8000/docs

### Step 5: Start the Frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at: http://localhost:5173

## Running Tests
```bash
python tests/test_api.py
```

## Architecture
User → React Frontend (5173) → FastAPI Backend (8000) → Ollama LLM (11434) → Response

## More changes to be pushed soon. Stay tuned. 