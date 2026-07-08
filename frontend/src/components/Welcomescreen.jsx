// frontend/src/components/WelcomeScreen.jsx
//
// Welcome / empty state.
// Shows a greeting, the shared composer, and clickable suggestion items.
// Clicking any item calls onSuggestionClick(text), which pre-fills the input.

const SUGGESTIONS = [
  "How do I register for a course?",
  "When are the final examinations?",
  "How can I pay my tuition fees?",
  "How do I apply for hostel accommodation?",
  "What are the library opening hours?",
  "I need help with ICT support.",
  "Show me the academic calendar.",
  "What are the student conduct regulations?",
];

export default function WelcomeScreen({ onSuggestionClick, composer }) {
  return (
    <div className="welcome">
      <div className="welcome__hero">
        <h1 className="welcome__title">What can I help you with today?</h1>
        <p className="welcome__subtitle">
          Ask me about course registration, examinations, fees, library services,
          hostel applications, and more.
        </p>
      </div>

      <div className="welcome__composer">
        {composer}
      </div>

      <ul className="suggestions-list">
        {SUGGESTIONS.map((text) => (
          <li key={text}>
            <button
              className="suggestion-btn"
              onClick={() => onSuggestionClick(text)}
              aria-label={`Ask: ${text}`}
            >
              <span>{text}</span>
              <span className="suggestion-btn__arrow" aria-hidden="true">-&gt;</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
