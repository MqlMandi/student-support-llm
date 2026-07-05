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

export default function ChatMessage({ msg }) {
  const isUser = msg.role === "user";

  return (
    <div className={`msg-row ${isUser ? "msg-row--user" : "msg-row--assistant"}`}>

      {/* Teal "ASSISTANT" label — only shown for assistant messages */}
      {!isUser && (
        <span className="msg-label">Assistant</span>
      )}

      <div className={`msg-bubble ${isUser ? "msg-bubble--user" : "msg-bubble--assistant"}`}>
        <p className="msg-text">{msg.text}</p>
        {msg.time && (
          <time className="msg-time">{msg.time}</time>
        )}
      </div>

    </div>
  );
}