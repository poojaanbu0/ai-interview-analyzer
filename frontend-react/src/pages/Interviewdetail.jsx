import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import StatusBadge from "../components/StatusBadge.jsx";
import { useFetch } from "../hooks.js";
import { formatDateTime, hasStarted, hrStatus } from "../utils.js";

export default function InterviewDetail() {
  const { id } = useParams();
  const { data: interview, error, reload } = useFetch(() => api.getInterview(id), [id]);
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");

  async function toggleCancel() {
    setBusy(true);
    setActionError("");
    try {
      await api.updateInterview(id, { status: interview.status === "open" ? "closed" : "open" });
      reload();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setBusy(false);
    }
  }

  // 404 = interview does not exist or belongs to another HR
  if (error) {
    return (
      <>
        <p className="error">{error}</p>
        <Link to="/hr">Back to my interviews</Link>
      </>
    );
  }
  if (!interview) return <p className="muted">Loading...</p>;

  const a = interview.assignment;
  const started = hasStarted(interview);

  return (
    <>
      <div className="page-title">
        <div>
          <h1>{interview.job_title}</h1>
          <StatusBadge value={hrStatus(interview)} />
        </div>
        <div className="actions">
          <Link className="btn btn-secondary" to="/hr">
            Back
          </Link>
          {!started && (
            <>
              <Link className="btn btn-secondary" to={`/hr/interviews/${id}/edit`}>
                Edit
              </Link>
              <button className="btn btn-secondary" disabled={busy} onClick={toggleCancel}>
                {interview.status === "open" ? "Cancel interview" : "Reopen interview"}
              </button>
            </>
          )}
        </div>
      </div>

      {actionError && <p className="error">{actionError}</p>}
      {started && <p className="muted">The candidate has started this interview, so it can no longer be edited or cancelled.</p>}

      <div className="detail-grid">
        <section className="card">
          <h2>Candidate</h2>
          {a ? (
            <dl className="kv">
              <dt>Name</dt>
              <dd>{a.candidate.name}</dd>
              <dt>ID</dt>
              <dd>{a.candidate.candidate_code}</dd>
              <dt>Email</dt>
              <dd>{a.candidate.email}</dd>
              <dt>Phone</dt>
              <dd>{a.candidate.phone || "-"}</dd>
            </dl>
          ) : (
            <p className="muted">No candidate assigned.</p>
          )}
        </section>

        <section className="card">
          <h2>Schedule and progress</h2>
          <dl className="kv">
            <dt>Scheduled for</dt>
            <dd>{formatDateTime(a?.scheduled_at)}</dd>
            <dt>Interview</dt>
            <dd>{a?.session_status ? <StatusBadge value={a.session_status} /> : "Not started"}</dd>
            <dt>Report</dt>
            <dd>{a?.has_report ? "Ready" : "Not available yet"}</dd>
          </dl>
        </section>
      </div>

      {a?.candidate_summary && (
        <section className="card">
          <h2>Candidate summary</h2>
          <p className="muted">Visible to HR only.</p>
          <p className="text-block">{a.candidate_summary}</p>
        </section>
      )}

      <section className="card">
        <h2>Job details</h2>
        <div className="meta">
          {interview.location && <span className="chip">{interview.location}</span>}
          {interview.employment_type && <span className="chip">{interview.employment_type}</span>}
          {interview.experience_level && <span className="chip">{interview.experience_level}</span>}
        </div>
        <h3>Description</h3>
        <p className="text-block">{interview.job_description}</p>
        {interview.requirements && (
          <>
            <h3>Requirements</h3>
            <p className="text-block">{interview.requirements}</p>
          </>
        )}
      </section>
    </>
  );
}