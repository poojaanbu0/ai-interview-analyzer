import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import StatusBadge from "../components/StatusBadge.jsx";
import { useFetch } from "../hooks.js";
import { candidateLabel, formatDateTime, hasStarted, hrStatus } from "../utils.js";

export default function HRDashboard() {
  const { data: interviews, loading, error, reload } = useFetch(() => api.listInterviews());
  const [busyId, setBusyId] = useState(null);
  const [actionError, setActionError] = useState("");

  async function toggleCancel(interview) {
    setBusyId(interview.interview_id);
    setActionError("");
    try {
      await api.updateInterview(interview.interview_id, { status: interview.status === "open" ? "closed" : "open" });
      reload();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <>
      <div className="page-title">
        <h1>My interviews</h1>
        <Link className="btn" to="/hr/interviews/new">
          Create interview
        </Link>
      </div>

      {error && <p className="error">{error}</p>}
      {actionError && <p className="error">{actionError}</p>}
      {loading && !interviews && <p className="muted">Loading...</p>}
      {interviews && interviews.length === 0 && (
        <p className="muted">You have not created any interviews yet. Click "Create interview" to assign one to a candidate.</p>
      )}

      <div className="list">
        {interviews?.map((interview) => {
          const a = interview.assignment;
          return (
            <article className="card item" key={interview.interview_id}>
              <div className="item-main">
                <h2>{interview.job_title}</h2>
                <div className="meta">
                  <StatusBadge value={hrStatus(interview)} />
                  {a?.has_report && <span className="status status-completed">Report ready</span>}
                </div>
                {a ? (
                  <>
                    <p className="muted">Candidate: {candidateLabel(a.candidate)}</p>
                    <p className="muted">Scheduled: {formatDateTime(a.scheduled_at)}</p>
                  </>
                ) : (
                  <p className="muted">No candidate assigned</p>
                )}
              </div>
              <div className="actions">
                <Link className="btn btn-secondary" to={`/hr/interviews/${interview.interview_id}`}>
                  View
                </Link>
                <button
                  className="btn btn-secondary"
                  disabled={busyId === interview.interview_id || hasStarted(interview)}
                  title={hasStarted(interview) ? "The candidate has already started" : ""}
                  onClick={() => toggleCancel(interview)}
                >
                  {interview.status === "open" ? "Cancel interview" : "Reopen interview"}
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </>
  );
}