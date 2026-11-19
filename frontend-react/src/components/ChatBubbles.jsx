export default function ChatBubbles({ conversations = [] }) {
  if (!conversations.length) {
    return <p className="muted">No conversation data available.</p>;
  }

  return (
    <div className="chat-window">
      {conversations.map((item, idx) => (
        <div key={idx} className="chat-turn">
          {/* Agent question — left */}
          <div className="chat-row chat-row-left">
            <div className="chat-avatar chat-avatar-agent">AI</div>
            <div className="chat-bubble chat-bubble-left">
              <p>{item.question}</p>
            </div>
          </div>

          {/* Candidate answer — right */}
          <div className="chat-row chat-row-right">
            <div className="chat-bubble chat-bubble-right">
              <p>{item.answer || item.transcript || "No response recorded."}</p>
            </div>
            <div className="chat-avatar chat-avatar-candidate">
              {item.candidate_initial || "C"}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
