// frontend/src/components/ChatMessage.jsx
//
// Renders a single message bubble.
//
// User messages:
//   — Right-aligned, charcoal (#27251e) fill, white text.
//   — Flat bottom-right corner to suggest the message "comes from" the user.
//
// Assistant messages:
//   — Left-aligned, white card with pebble border and subtle shadow.
//   — Preceded by a small "ASSISTANT" label in deep teal (#016a71).
//     This is the ONLY place the teal accent appears in the UI.
//   — Flat top-left corner sits visually beneath the label.
//
// Styles live in App.css.

import { useState } from "react";
import axios from "axios";
import { FileText, ThumbsUp, Minus, ThumbsDown } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function ChatMessage({ msg }) {
  const isUser = msg.role === "user";
  const [rating, setRating] = useState(null);

  const handleFeedback = async (value) => {
    if (rating) return; // already rated
    setRating(value);
    try {
      await axios.post(`${API_URL}/api/feedback`, {
        question: msg.question || "Unknown question",
        answer: msg.text,
        rating: value
      });
    } catch (err) {
      console.error("Failed to submit feedback", err);
    }
  };

  return (
    <div className={`msg-row ${isUser ? "msg-row--user" : "msg-row--assistant"}`}>

      {/* Teal "ASSISTANT" label — only shown for assistant messages */}
      {!isUser && (
        <span className="msg-label">Assistant</span>
      )}

      <div className={`msg-bubble ${isUser ? "msg-bubble--user" : "msg-bubble--assistant"}`}>
        {msg.attachedFile && (
          <div className="msg-file-badge">
            <FileText size={14} />
            <span>{msg.attachedFile}</span>
          </div>
        )}
        <p className="msg-text">{msg.text}</p>
        {msg.time && (
          <time className="msg-time">{msg.time}</time>
        )}
      </div>

      {/* Feedback UI */}
      {!isUser && (
        <div className="msg-feedback">
          {rating ? (
            <span className="feedback-thanks">Thank you for rating: {rating}</span>
          ) : (
            <div className="feedback-buttons">
              <button onClick={() => handleFeedback("Good")} aria-label="Good" className="feedback-btn"><ThumbsUp size={14} /></button>
              <button onClick={() => handleFeedback("Average")} aria-label="Average" className="feedback-btn"><Minus size={14} /></button>
              <button onClick={() => handleFeedback("Poor")} aria-label="Poor" className="feedback-btn"><ThumbsDown size={14} /></button>
            </div>
          )}
        </div>
      )}

    </div>
  );
}