import { useState } from "react";
import { api } from "../api.js";
import { useFetch } from "../hooks.js";
import { candidateLabel, fromInputValue } from "../utils.js";

export default function AssignCandidateModal({ roomId, onClose, onAssigned }) {
  const candidates = useFetch(() => api.listCandidates());
  const [candidateId, setCandidateId] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!candidateId) { setError("Select a candidate"); return; }
    if (!file) { setError("Upload a resume (PDF or DOCX)"); return; }
    if (!scheduledAt) { setError("Select a scheduled time"); return; }

    setBusy(true);
    const form = new FormData();
    form.append("candidate_id", candidateId);
    form.append("resume", file);
    form.append("scheduled_at", fromInputValue(scheduledAt));

    try {
      const result = await api.assignCandidate(roomId, form);
      setSummary(result.candidate_summary);
      onAssigned?.();
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Assign Candidate</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {summary ? (
          <div className="modal-body">
            <div className="summary-result">
              <h3>✓ Candidate Assigned</h3>
              <p className="muted" style={{ marginBottom: "0.75rem" }}>
                Resume processed and summary generated:
              </p>
              <div className="summary-box">{summary}</div>
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={onClose}>Done</button>
            </div>
          </div>
        ) : (
          <form className="modal-body" onSubmit={handleSubmit}>
            <label>
              Candidate
              <select
                value={candidateId}
                onChange={(e) => setCandidateId(e.target.value)}
                required
              >
                <option value="">-- Select a candidate --</option>
                {candidates.data?.map((c) => (
                  <option key={c.user_id} value={c.user_id}>
                    {candidateLabel(c)}
                  </option>
                ))}
              </select>
              {candidates.loading && <span className="hint">Loading candidates...</span>}
            </label>

            <label>
              Resume (PDF or DOCX)
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => setFile(e.target.files[0] || null)}
                required
              />
            </label>

            <label>
              Scheduled Date & Time
              <input
                type="datetime-local"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
                required
              />
              <span className="hint">Shown in your local time zone</span>
            </label>

            {error && <p className="error">{error}</p>}

            <div className="modal-actions">
              <button className="btn" disabled={busy}>
                {busy ? (
                  <span className="processing">
                    <span className="spinner" />
                    Processing resume...
                  </span>
                ) : (
                  "Assign & Process Resume"
                )}
              </button>
              <button type="button" className="btn btn-secondary" onClick={onClose} disabled={busy}>
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
