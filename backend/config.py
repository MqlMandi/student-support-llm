import os
from dotenv import load_dotenv

# Load from the root .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("GENERATION_MODEL_NAME", "llama3.2:1b")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "nomic-embed-text:latest")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
APP_NAME = os.getenv("APP_NAME", "Student Support LLM Assistant")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")