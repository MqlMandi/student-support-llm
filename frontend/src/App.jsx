// frontend/src/App.jsx
// Student Support — University AI Assistant
// IS 365 | University of Dar es Salaam
//
// Folder structure (create the components/ folder first):
//   frontend/src/
//   ├── App.jsx          ← this file
//   ├── App.css
//   ├── index.css
//   └── components/
//       ├── WelcomeScreen.jsx
//       ├── ChatMessage.jsx
//       └── TypingIndicator.jsx

import { useState, useRef, useEffect, useCallback } from "react";
import axios from "axios";
import "./App.css";
import WelcomeScreen from "./components/WelcomeScreen";
import ChatMessage from "./components/ChatMessage";
import TypingIndicator from "./components/TypingIndicator";

const API_URL = "http://localhost:8000";

function getTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function App() {
  const [input, setInput]       = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);

  const bottomRef = useRef(null);
  const inputRef  = useRef(null);
  const hasMessages = messages.length > 0;

  // ── Auto-scroll to the latest message ────────────────────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // ── Auto-resize textarea as the user types ────────────────────────────────────
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }, [input]);

  // ── Send question to FastAPI backend ──────────────────────────────────────────
  const send = useCallback(async (text) => {
    const q = (text ?? input).trim();
    if (!q || loading) return;

    setError(null);
    setLoading(true);
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: q, time: getTime() }]);

    try {
      const res = await axios.post(`${API_URL}/ask`, { question: q });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.data.answer, time: getTime() },
      ]);
    } catch (err) {
      let msg = "Something went wrong. Please try again.";
      if (err.code === "ERR_NETWORK")        msg = "Cannot reach the server — make sure the backend is running.";
      else if (err.response?.status === 503) msg = "The AI model is unavailable — make sure Ollama is running.";
      else if (err.response?.status === 504) msg = "The model timed out. Try a shorter question.";
      else if (err.response?.status === 400) msg = err.response.data.detail ?? "Invalid request.";
      setError(msg);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [input, loading]);

  // ── Keyboard: Enter sends, Shift+Enter adds a new line ────────────────────────
  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey && !loading) {
      e.preventDefault();
      send();
    }
  };

  // ── Pre-fill input from a welcome suggestion ──────────────────────────────────
  const pickSuggestion = (suggestion) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  // Derive button visual state
  const canSend   = input.trim().length > 0;
  const btnState  = loading ? "loading" : canSend ? "active" : "idle";

  return (
    <div className="app-shell">

      {/* ══ HEADER ════════════════════════════════════════════════════════════ */}
      <header className="app-header">
        <div className="app-header__brand">
          <span className="app-header__title">Student Support</span>
          <span className="app-header__sep" aria-hidden="true" />
          <span className="app-header__model">Llama 3.2 · local</span>
        </div>
        <span className="app-header__badge">UDSM</span>
      </header>

      {/* ══ CHAT AREA ═════════════════════════════════════════════════════════ */}
      <main className="chat-area">
        {!hasMessages ? (
          // Welcome screen — shown before any messages
          <WelcomeScreen onSuggestionClick={pickSuggestion} />
        ) : (
          // Chat messages
          <div className="messages" role="log" aria-live="polite" aria-label="Conversation">
            {messages.map((msg, i) => (
              <ChatMessage key={i} msg={msg} />
            ))}
            {loading && <TypingIndicator />}
            {/* Invisible anchor scrolled into view on each new message */}
            <div ref={bottomRef} />
          </div>
        )}
      </main>

      {/* ══ ERROR NOTICE ══════════════════════════════════════════════════════ */}
      {error && (
        <div className="error-notice" role="alert">
          <p className="error-notice__text">{error}</p>
          <button
            className="error-notice__dismiss"
            onClick={() => setError(null)}
            aria-label="Dismiss error"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* ══ FOOTER / INPUT ════════════════════════════════════════════════════ */}
      <footer className="app-footer">
        <div className="input-card">
          <textarea
            ref={inputRef}
            className="input-card__field"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask about courses, exams, fees, hostel..."
            rows={1}
            disabled={loading}
            aria-label="Your question"
            aria-describedby="footer-hint"
          />

          {/* 28×28 circle submit button — per design system spec */}
          <button
            className={`submit-btn submit-btn--${btnState}`}
            onClick={() => send()}
            disabled={!canSend || loading}
            aria-label={loading ? "Sending" : "Send question"}
          >
            {loading ? (
              <span className="submit-spinner" aria-hidden="true" />
            ) : (
              /* Upward arrow icon — same as Perplexity's submit button */
              <svg
                viewBox="0 0 16 16"
                fill="none"
                className="submit-icon"
                aria-hidden="true"
              >
                <path
                  d="M8 13V3M3.5 7.5L8 3 12.5 7.5"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </button>
        </div>

        <p className="footer-hint" id="footer-hint">
          <kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for new line
        </p>
      </footer>

    </div>
  );
}