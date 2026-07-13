// frontend/src/App.jsx
// Student Support - University AI Assistant
// IS 365 | University of Dar es Salaam

import { useState, useRef, useEffect, useCallback } from "react";
import axios from "axios";
import "./App.css";
import WelcomeScreen from "./components/WelcomeScreen";
import ChatMessage from "./components/ChatMessage";
import TypingIndicator from "./components/TypingIndicator";
import { FileText, X, Loader2, Paperclip, RefreshCw, Globe, GraduationCap, Camera } from "lucide-react";

const API_URL = "http://localhost:8000";

function getTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function App() {
  const [input, setInput]       = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  
  // File upload state
  const [sessionId, setSessionId] = useState(null);
  const [uploadedFilename, setUploadedFilename] = useState(null);
  const [uploadingFile, setUploadingFile] = useState(false);

  const bottomRef = useRef(null);
  const inputRef  = useRef(null);
  const fileInputRef = useRef(null);
  const hasMessages = messages.length > 0;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }, [input]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingFile(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API_URL}/api/upload`, formData);
      setSessionId(res.data.session_id);
      setUploadedFilename(res.data.filename);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to upload file.");
    } finally {
      setUploadingFile(false);
      e.target.value = null; // reset input
    }
  };

  const handleRemoveFile = async () => {
    if (sessionId) {
      try {
        await axios.delete(`${API_URL}/api/session/${sessionId}`);
      } catch (err) {
        console.error("Failed to delete session", err);
      }
    }
    setSessionId(null);
    setUploadedFilename(null);
  };

  const startNewChat = async () => {
    await handleRemoveFile();
    setMessages([]);
    setError(null);
    setInput("");
  };

  const send = useCallback(async (text) => {
    const q = (text ?? input).trim();
    if (!q || loading) return;

    setError(null);
    setLoading(true);
    setInput("");
    
    // Snapshot the file to the chat log and consume it from the composer UI
    const currentFile = uploadedFilename;
    setUploadedFilename(null);
    
    setMessages((prev) => [...prev, { role: "user", text: q, time: getTime(), attachedFile: currentFile }]);

    try {
      const payload = { question: q };
      if (sessionId) payload.session_id = sessionId;
      
      const res = await axios.post(`${API_URL}/ask`, payload);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.data.answer, time: getTime() },
      ]);
    } catch (err) {
      let msg = "Something went wrong. Please try again.";
      if (err.code === "ERR_NETWORK")        msg = "Cannot reach the server \u2014 make sure the backend is running.";
      else if (err.response?.status === 503) msg = "The AI model is unavailable \u2014 make sure Ollama is running.";
      else if (err.response?.status === 504) msg = "The model timed out. Try a shorter question.";
      else if (err.response?.status === 400) msg = err.response.data.detail ?? "Invalid request.";
      setError(msg);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [input, loading, sessionId]);

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey && !loading) {
      e.preventDefault();
      send();
    }
  };

  const pickSuggestion = (suggestion) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  const canSend   = input.trim().length > 0;
  const btnState  = loading ? "loading" : canSend ? "active" : "idle";

  const composer = (
    <>
      {uploadedFilename && (
        <div className="file-badge">
          <span className="file-badge__name" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <FileText size={14} /> {uploadedFilename}
          </span>
          <button className="file-badge__remove" onClick={handleRemoveFile} aria-label="Remove file">
            <X size={14} />
          </button>
        </div>
      )}
      <div className="input-card">
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          accept=".txt,.md,.pdf,.docx"
          onChange={handleFileUpload}
        />
        <button 
          className="attach-btn" 
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadingFile || loading}
          aria-label="Attach file"
        >
          {uploadingFile ? <Loader2 size={16} className="spin" /> : <Paperclip size={16} />}
        </button>

        <textarea
          ref={inputRef}
          className="input-card__field"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={uploadedFilename ? `Ask about ${uploadedFilename}...` : "Ask about courses, exams, fees, hostel..."}
          rows={1}
          disabled={loading}
          aria-label="Your question"
          aria-describedby="footer-hint"
        />

        <button
          className={`submit-btn submit-btn--${btnState}`}
          onClick={() => send()}
          disabled={!canSend || loading}
          aria-label={loading ? "Sending" : "Send question"}
        >
          {loading ? (
            <span className="submit-spinner" aria-hidden="true" />
          ) : (
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
        <kbd>Enter</kbd> to send &middot; <kbd>Shift+Enter</kbd> for new line
      </p>
    </>
  );

  return (
    <div className="app-shell">
      <aside className="app-sidebar" aria-label="Navigation">
        <div className="app-sidebar__top">
          <div className="app-sidebar__brand" aria-label="Student Support">
            <span className="brand-mark" aria-hidden="true">S</span>
            <span className="sidebar-collapse" aria-hidden="true">[]</span>
          </div>

          <nav className="sidebar-nav" aria-label="Primary">
            <button
              className="sidebar-nav__item sidebar-nav__item--active"
              type="button"
              onClick={startNewChat}
            >
              <RefreshCw size={16} />
              <span>New Chat</span>
            </button>

            <button
              className="sidebar-nav__item"
              type="button"
              onClick={() => window.location.href = "https://udsm.ac.tz/"}
            >
              <Globe size={16} />
              <span>UDSM Website</span>
            </button>
            
            <button 
              className="sidebar-nav__item" 
              type="button"
              onClick={() => window.location.href = "https://aris3.udsm.ac.tz/index.php?r=student%2Fuser%2Flogin"}
            >
              <GraduationCap size={16} />
              <span>ARIS 3</span>
            </button>

            <button 
              className="sidebar-nav__item" 
              type="button"
              onClick={() => window.location.href = "https://www.instagram.com/udsmofficial?igsh=dGEzdWVwOHJ4bW1q"}
            >
              <Camera size={16} />
              <span>UDSM Socials</span>
            </button>
            
          </nav>

          <span className="sidebar-empty">No recent threads</span>
        </div>

        <button className="sidebar-signin" type="button">
          <span className="signin-dot" aria-hidden="true" />
          <span>Sign In</span>
          <span aria-hidden="true">&gt;</span>
        </button>
      </aside>

      <div className="app-main">
        <header className="app-header">
          <div className="app-header__brand">
            <span className="app-header__title">Student Support</span>
            <span className="app-header__sep" aria-hidden="true" />
            <span className="app-header__model">Llama 3.1 &middot; local</span>
          </div>
          <span className="app-header__badge">UDSM</span>
        </header>

        <nav className="top-topics" aria-label="Topics">
          <button type="button">Discover</button>
          <button type="button">Finance</button>
          <button type="button">Health</button>
          <button type="button">Academic</button>
          <button type="button">Patents</button>
        </nav>

        <main className="chat-area">
          {!hasMessages ? (
            <WelcomeScreen onSuggestionClick={pickSuggestion} composer={composer} />
          ) : (
            <div className="messages" role="log" aria-live="polite" aria-label="Conversation">
              {messages.map((msg, i) => (
                <ChatMessage key={i} msg={msg} />
              ))}
              {loading && <TypingIndicator />}
              <div ref={bottomRef} />
            </div>
          )}
        </main>

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

        {hasMessages && <footer className="app-footer">{composer}</footer>}
      </div>
    </div>
  );
}
