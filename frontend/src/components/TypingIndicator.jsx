// frontend/src/components/TypingIndicator.jsx
//
// Shown while the LLM is generating a response.
//
// Design: three skeleton bars animating with a shimmer effect — directly
// inspired by Perplexity's loading state (Status Card skeletons in DESIGN.md).
// Bars use the --color-skeleton (#f0eeea) fill with cascading animation delays.
// The "ASSISTANT" label in teal matches ChatMessage for visual consistency.
//
// Styles live in App.css.

export default function TypingIndicator() {
  return (
    <div
      className="msg-row msg-row--assistant"
      role="status"
      aria-label="Assistant is thinking"
    >
      <span className="msg-label" aria-hidden="true">Assistant</span>

      <div className="msg-bubble msg-bubble--assistant typing-bubble">
        <span className="skeleton-bar" />
        <span className="skeleton-bar" />
        <span className="skeleton-bar" />
      </div>
    </div>
  );
}