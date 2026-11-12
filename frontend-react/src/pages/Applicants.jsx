import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, downloadResume } from "../api.js";
import StatusBadge from "../components/StatusBadge.jsx";
import { useFetch } from "../hooks.js";
import { formatDate } from "../utils.js";

export default function Applicants() {
  const { id } = useParams();
  const job = useFetch(() => api.getInterview(id), [id]);
  const applicants = useFetch(() => api.listApplicants(id), [id]);
  const [downloadError, setDownloadError] = useState("");

  async function handleDownload(applicationId) {
    setDownloadError("");
    try {
      await downloadResume(applicationId);
    } catch (err) {
      setDownloadError(err.message);
    }
  }

  // 404 = job does not exist or belongs to another HR
  if (job.error) {
    return (
      <>
        <p className="error">{job.error}</p>
        <Link to="/hr">Back to my jobs</Link>
      </>
    );
  }

  return (
    <>
      <div className="page-title">
        <div>
          <h1>{job.data ? job.data.job_title : "Applicants"}</h1>
          {job.data && <StatusBadge value={job.data.status} />}
        </div>
        <Link className="btn btn-secondary" to="/hr">
          Back to my jobs
        </Link>
      </div>

      {applicants.error && <p className="error">{applicants.error}</p>}
      {downloadError && <p className="error">{downloadError}</p>}
      {applicants.loading && !applicants.data && <p className="muted">Loading...</p>}
      {applicants.data && applicants.data.length === 0 && <p className="muted">No one has applied yet.</p>}

      {applicants.data && applicants.data.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Applied</th>
                <th>Application</th>
                <th>Interview</th>
                <th>Report</th>
                <th>Resume</th>
              </tr>
            </thead>
            <tbody>
              {applicants.data.map((a) => (
                <tr key={a.application_id}>
                  <td>
                    <strong>{a.candidate_name}</strong>
                    <br />
                    <span className="muted">{a.candidate_email}</span>
                  </td>
                  <td>{formatDate(a.applied_at)}</td>
                  <td>
                    <StatusBadge value={a.status} />
                  </td>
                  <td>{a.session_status ? <StatusBadge value={a.session_status} /> : <span className="muted">Not attended</span>}</td>
                  <td>{a.has_report ? <span className="status status-completed">Ready</span> : <span className="muted">-</span>}</td>
                  <td>
                    <button className="btn btn-secondary" onClick={() => handleDownload(a.application_id)}>
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}