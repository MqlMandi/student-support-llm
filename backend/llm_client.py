# backend/llm_client.py
#
# Contains:
#   1. SYSTEM_PROMPT       — tells the model who it is
#   2. _call_ollama()      — sends any prompt to Ollama and returns the text
#   3. _load_faq()         — parses faq.txt into a {section_name: text} dict
#   4. _score()            — scores one FAQ section against a student question
#   5. find_relevant_faq() — returns the top-N most relevant sections
#   6. ask_llm()           — raw call with no FAQ context (fallback)
#   7. ask_llm_with_rag()  — injects retrieved FAQ context into the prompt

import os
import re
import httpx
from config import OLLAMA_BASE_URL, MODEL_NAME

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a helpful and accurate University Student Support Assistant \
for the University of Dar es Salaam (UDSM).

You help students with questions about:
- Course registration and academic regulations
- Examination rules and grading
- Academic calendar, semester dates and deadlines
- Tuition fees and university costs
- Accommodation and hostel
- Library services
- Healthcare and NHIF
- Counselling and mental health
- ICT support and computing
- Student governance (DARUSO)
- Transport services
- Catering and food
- Sports and games
- Financial support (HESLB, scholarships)
- Student conduct and discipline
- Student grievances and appeals
- Orientation for new students
- Students with special needs
- International students
- Spiritual affairs
- Career guidance and entrepreneurship

Rules:
1. When university document excerpts are provided below, base your answer primarily on them.
2. Be specific — mention actual dates, fees, and contact details when available in the context.
3. If the provided excerpts do not fully answer the question, say so clearly.
4. If you are unsure about something, recommend that the student visit the relevant office.
5. Do not invent policies, fees, dates, or phone numbers.
6. Be concise, friendly, and professional.
"""

# ── Ollama helper ──────────────────────────────────────────────────────────────

def _call_ollama(prompt: str, timeout: float = 90.0) -> str:
    """
    Send a prompt to the local Ollama API and return the model's response text.
    Raises typed exceptions so the caller can map them to HTTP error codes.
    """
    url     = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "No response received from the model.")

    except httpx.ConnectError:
        raise ConnectionError(
            "Cannot connect to Ollama. Make sure Ollama is running "
            "('ollama serve' in a terminal)."
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


# ── FAQ retrieval ──────────────────────────────────────────────────────────────

# Stop words: common English words that carry no useful signal for matching.
_STOPWORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "for", "of",
    "and", "or", "but", "not", "with", "from", "by", "as", "are", "was",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "can",
    "i", "my", "me", "we", "our", "you", "your", "they", "their",
    "he", "she", "his", "her", "this", "that", "these", "those",
    "what", "when", "where", "how", "who", "which", "why", "please",
    "tell", "about", "am", "if", "any", "some", "there", "up",
}

def _load_faq(faq_path: str) -> dict[str, str]:
    """
    Parse the FAQ text file into an ordered dict of {SECTION_NAME: section_text}.

    The file uses the format:
        === SECTION NAME ===
        Content...

        === NEXT SECTION ===
        More content...

    Lines starting with '#' are treated as comments and ignored.
    Returns an empty dict if the file does not exist.
    """
    if not os.path.exists(faq_path):
        return {}

    sections: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []

    with open(faq_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip()

            # Skip comment lines
            if line.startswith("#"):
                continue

            # Detect a section header like === SECTION NAME ===
            match = re.match(r"^===\s*(.+?)\s*===$", line)
            if match:
                # Save the previous section (if any)
                if current_name is not None:
                    sections[current_name] = "\n".join(current_lines).strip()
                current_name = match.group(1).strip()
                current_lines = []
            else:
                if current_name is not None:
                    current_lines.append(line)

    # Save the last section
    if current_name is not None:
        sections[current_name] = "\n".join(current_lines).strip()

    return sections


def _score(section_text: str, question: str) -> float:
    """
    Score a FAQ section against a student question using word-overlap.

    Algorithm (Bag-of-Words):
      1. Tokenise the question into lowercase words.
      2. Remove stop words.
      3. For each meaningful word, check if it appears anywhere in the
         section text (case-insensitive).
      4. Score = matched words / total meaningful words in the question.

    Returns a float between 0.0 (no match) and 1.0 (perfect match).
    Returns 0.0 if the question has no meaningful words after stop-word removal.
    """
    # Tokenise question: split on any non-alphanumeric character
    raw_words  = re.findall(r"[a-zA-Z0-9]+", question.lower())
    q_words    = [w for w in raw_words if w not in _STOPWORDS and len(w) > 1]

    if not q_words:
        return 0.0

    section_lower = section_text.lower()
    matched = sum(1 for w in q_words if w in section_lower)
    return matched / len(q_words)


def find_relevant_faq(
    question: str,
    faq_path: str = "faq.txt",
    top_k: int = 2,
    min_score: float = 0.15,
) -> str:
    """
    Find the most relevant FAQ sections for a given student question.

    Steps:
      1. Load and parse the FAQ file into sections.
      2. Score every section against the question with _score().
      3. Sort sections by score (highest first).
      4. Return the text of the top_k sections whose score ≥ min_score,
         formatted as clearly labelled context blocks.

    Returns an empty string if no section clears the minimum score threshold.

    Parameters:
        question  The raw student question text.
        faq_path  Path to the FAQ text file (default: "faq.txt").
        top_k     Maximum number of sections to retrieve (default: 2).
        min_score Minimum relevance score to include a section (default: 0.15).
                  Raise this to be more selective; lower it to be more permissive.
    """
    sections = _load_faq(faq_path)
    if not sections:
        return ""

    # Score every section
    scored = [
        (name, text, _score(text, question))
        for name, text in sections.items()
    ]

    # Sort by score descending
    scored.sort(key=lambda x: x[2], reverse=True)

    # Keep only sections that clear the threshold
    relevant = [(name, text) for name, text, score in scored if score >= min_score]
    relevant = relevant[:top_k]

    if not relevant:
        return ""

    # Format retrieved sections as labelled context blocks
    blocks = []
    for name, text in relevant:
        blocks.append(f"[FAQ: {name}]\n{text}")

    return "\n\n---\n\n".join(blocks)


# ── Public LLM functions ───────────────────────────────────────────────────────

def ask_llm(question: str) -> str:
    """
    Send a question directly to the LLM with no FAQ context.
    Used as a fallback when find_relevant_faq() returns nothing useful.
    """
    prompt = f"{SYSTEM_PROMPT}\n\nStudent question: {question}\n\nAssistant:"
    return _call_ollama(prompt)


def ask_llm_with_rag(question: str, faq_path: str = "faq.txt") -> str:
    """
    Retrieve the most relevant FAQ sections for the question, inject them
    into the prompt, and return the LLM's grounded answer.

    If no relevant FAQ sections are found, falls back to ask_llm().
    Uses a longer timeout (120 s) because the augmented prompt is larger.
    """
    context = find_relevant_faq(question, faq_path=faq_path)

    if not context:
        # No relevant FAQ content found — use the model's general knowledge
        return ask_llm(question)

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        "The following excerpts from official UDSM documents are relevant "
        "to the student's question. Use them to give an accurate, specific answer:\n\n"
        f"{context}\n\n"
        "---\n\n"
        f"Student question: {question}\n\n"
        "Answer based on the documents above. If the documents do not fully "
        "cover the question, say so and direct the student to the relevant office:\n\n"
        "Assistant:"
    )

    return _call_ollama(prompt, timeout=120.0)