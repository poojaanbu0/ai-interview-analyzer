import { Link, useLocation, useNavigate } from "react-router-dom";
import { api } from "../api.js";
import StatusBadge from "../components/StatusBadge.jsx";
import { useFetch } from "../hooks.js";
import { formatDate } from "../utils.js";

export default function MyApplications() {
  const navigate = useNavigate();
  const location = useLocation();
  const appliedTo = location.state?.appliedTo; // set by JobCard after a successful application
  const { data: applications, loading, error } = useFetch(() => api.myApplications());

  return (
    <>
      <div className="page-title">
        <h1>My applications</h1>
      </div>

      {appliedTo && (
        <p className="banner">
          Your application for <strong>{appliedTo}</strong> was submitted. You can attend the interview now.
        </p>
      )}

      {error && <p className="error">{error}</p>}
      {loading && !applications && <p className="muted">Loading...</p>}
      {applications && applications.length === 0 && (
        <p className="muted">
          You have not applied to any jobs yet. <Link to="/candidate">Browse jobs</Link>
        </p>
      )}

      <div className="list">
        {applications?.map((app) => (
          <article className="card item" key={app.application_id}>
            <div className="item-main">
              <h2>{app.job_title}</h2>
              <div className="meta">
                <StatusBadge value={app.status} />
                {app.session_status && <StatusBadge value={app.session_status} />}
              </div>
              <p className="muted">Applied {formatDate(app.applied_at)}</p>
            </div>
            <div className="actions">
              {app.can_attend ? (
                <button className="btn" onClick={() => navigate(`/candidate/interview/${app.application_id}`)}>
                  {app.session_status === "in_progress" ? "Resume interview" : "Attend interview"}
                </button>
              ) : (
                <span className="muted">Interview completed</span>
              )}
            </div>
          </article>
        ))}
      </div>
    </>
  );
}