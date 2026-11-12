import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api.js";
import { formatDate, validateResume } from "../utils.js";

export default function JobCard({ job }) {
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleApply(e) {
    e.preventDefault();
    setError("");
    if (!file) return setError("Please choose your resume");
    const problem = validateResume(file);
    if (problem) return setError(problem);

    setBusy(true);
    try {
      await api.applyToJob(job.interview_id, file);
      // the new application (with its Attend button) is on the next page
      navigate("/candidate/applications", { state: { appliedTo: job.job_title } });
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <article className="card">
      <div className="item">
        <div className="item-main">
          <h2>{job.job_title}</h2>
          <div className="meta">
            {job.location && <span className="chip">{job.location}</span>}
            {job.employment_type && <span className="chip">{job.employment_type}</span>}
            {job.experience_level && <span className="chip">{job.experience_level}</span>}
            <span className="chip">Posted {formatDate(job.created_at)}</span>
          </div>
        </div>
        <div className="actions">
          {job.has_applied && <span className="status status-applied">Applied</span>}
          <button className="btn btn-secondary" onClick={() => setExpanded(!expanded)}>
            {expanded ? "Hide details" : "View details"}
          </button>
        </div>
      </div>

      {expanded && (
        <div>
          <h3>Job description</h3>
          <p className="text-block">{job.job_description}</p>
          {job.requirements && (
            <>
              <h3>Requirements</h3>
              <p className="text-block">{job.requirements}</p>
            </>
          )}

          {job.has_applied ? (
            <p className="muted">
              You have already applied. <Link to="/candidate/applications">Go to my applications</Link>
            </p>
          ) : (
            <form className="apply-form" onSubmit={handleApply}>
              <input type="file" accept=".pdf,.doc,.docx" onChange={(e) => setFile(e.target.files[0] || null)} />
              <button className="btn" disabled={busy}>
                {busy ? "Applying..." : "Apply with resume"}
              </button>
              {error && <p className="error">{error}</p>}
            </form>
          )}
        </div>
      )}
    </article>
  );
}