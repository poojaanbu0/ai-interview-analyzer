import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import StatusBadge from "../components/StatusBadge.jsx";
import { useFetch } from "../hooks.js";
import { formatDate } from "../utils.js";

export default function HRDashboard() {
  const { data: jobs, loading, error, reload } = useFetch(() => api.listInterviews());
  const [busyId, setBusyId] = useState(null);
  const [actionError, setActionError] = useState("");

  async function toggleStatus(job) {
    setBusyId(job.interview_id);
    setActionError("");
    try {
      await api.updateInterview(job.interview_id, { status: job.status === "open" ? "closed" : "open" });
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
        <h1>My jobs</h1>
        <Link className="btn" to="/hr/jobs/new">
          Create interview
        </Link>
      </div>

      {error && <p className="error">{error}</p>}
      {actionError && <p className="error">{actionError}</p>}
      {loading && !jobs && <p className="muted">Loading...</p>}
      {jobs && jobs.length === 0 && (
        <p className="muted">You have not created any interviews yet. Click "Create interview" to add your first job.</p>
      )}

      <div className="list">
        {jobs?.map((job) => (
          <article className="card item" key={job.interview_id}>
            <div className="item-main">
              <h2>{job.job_title}</h2>
              <div className="meta">
                <StatusBadge value={job.status} />
                {job.location && <span className="chip">{job.location}</span>}
                {job.employment_type && <span className="chip">{job.employment_type}</span>}
                {job.experience_level && <span className="chip">{job.experience_level}</span>}
              </div>
              <p className="muted">
                {job.applicant_count} {job.applicant_count === 1 ? "applicant" : "applicants"} · Created{" "}
                {formatDate(job.created_at)}
              </p>
            </div>
            <div className="actions">
              <Link className="btn btn-secondary" to={`/hr/jobs/${job.interview_id}/applicants`}>
                View applicants
              </Link>
              <button className="btn btn-secondary" disabled={busyId === job.interview_id} onClick={() => toggleStatus(job)}>
                {job.status === "open" ? "Close job" : "Reopen job"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </>
  );
}