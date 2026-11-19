export default function ViewToggle({ view, onToggle }) {
  return (
    <div className="view-toggle">
      <button
        className={`view-toggle-btn ${view === "card" ? "active" : ""}`}
        onClick={() => onToggle("card")}
        title="Card view"
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <rect x="1" y="1" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5"/>
          <rect x="10" y="1" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5"/>
          <rect x="1" y="10" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5"/>
          <rect x="10" y="10" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5"/>
        </svg>
      </button>
      <button
        className={`view-toggle-btn ${view === "table" ? "active" : ""}`}
        onClick={() => onToggle("table")}
        title="Table view"
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <line x1="1" y1="3" x2="17" y2="3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          <line x1="1" y1="9" x2="17" y2="9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          <line x1="1" y1="15" x2="17" y2="15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </button>
    </div>
  );
}
