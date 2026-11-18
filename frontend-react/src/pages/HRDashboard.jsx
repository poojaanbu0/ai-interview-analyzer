
import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import StatusBadge from "../components/StatusBadge.jsx";
import { useFetch } from "../hooks.js";
import {
  candidateLabel,
  formatDateTime,
  hrStatus,
} from "../utils.js";


function MetricBar({ label, value, max, suffix = "", description }) {
  const percentage =
    max > 0 ? Math.min((value / max) * 100, 100) : 0;

  return (
    <div className="metric-bar">
      <div className="metric-bar-header">
        <span>{label}</span>
        <strong>
          {value}{suffix}
        </strong>
      </div>

      <div className="metric-track">
        <div
          className="metric-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>

      {description && (
        <small className="muted">{description}</small>
      )}
    </div>
  );
}

function InterviewMetrics({ metrics }) {
  return (
    <div className="interview-metrics">
      <h4>Interview Metrics</h4>

      <MetricBar
        label="Questions answered"
        value={metrics.questions_answered ?? 0}
        max={5}
        suffix=" / 5"
        description="Number of completed interview questions"
      />

      <MetricBar
        label="Average speech rate"
        value={metrics.average_speech_rate ?? 0}
        max={200}
        suffix=" WPM"
        description="Words spoken per minute"
      />

      <MetricBar
        label="Filler words"
        value={metrics.total_filler_words ?? 0}
        max={20}
        description="Total filler words detected"
      />
    </div>
  );
}



function InterviewResponses({ responses = [] }) {
  return (
    <section className="interview-responses">
      <h4>Candidate Questions & Answers</h4>

      {responses.length === 0 ? (
        <p className="muted">No interview responses found.</p>
      ) : (
        responses.map((item) => {
          const speechMetrics = item.speech_metrics || {};

          return (
            <article
              className="response-card"
              key={item.question_number}
            >
              <p className="response-number">
                Question {item.question_number}
              </p>

              <h4>{item.question}</h4>

              <p className="response-label">Candidate's Answer</p>

              <p className="response-answer">
                {item.answer || "No answer recorded."}
              </p>

              <div className="response-metrics">
                <p className="response-label">Speech Metrics</p>

                <div className="interview-metrics">
                  <MetricBar
                    label="Speech Rate"
                    value={speechMetrics.speech_rate ?? 0}
                    max={200}
                    suffix=" WPM"
                    description="Words spoken per minute"
                  />

                  <MetricBar
                    label="Filler Words"
                    value={speechMetrics.filler_words ?? 0}
                    max={10}
                    description="Filler words detected in this answer"
                  />
                </div>
              </div>
            </article>
          );
        })
      )}
    </section>
  );
}


function InterviewReport({ report }) {
  const summary = report.report_data?.summary || {};
  const metrics = report.report_data?.metrics || {};

  return (
    <section className="card" style={{ marginTop: "16px" }}>
      <h3>Interview Report</h3>

      <p className="muted">
        Generated:{" "}
        {report.generated_at
          ? formatDateTime(report.generated_at)
          : "Not available"}
      </p>

      <h4>Overall Summary</h4>
      <p>{summary.overall_summary || "No summary available."}</p>

      <InterviewMetrics metrics={metrics} />
      <InterviewResponses responses={report.responses} />

      <h4>Key Strengths</h4>
      {summary.key_strengths?.length ? (
        <ul>
          {summary.key_strengths.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">No strengths recorded.</p>
      )}

      <h4>Improvement Areas</h4>
      {summary.improvement_areas?.length ? (
        <ul>
          {summary.improvement_areas.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">No improvement areas recorded.</p>
      )}

      <h4>Technical Topics</h4>
      {summary.technical_topics?.length ? (
        <ul>
          {summary.technical_topics.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">No technical topics recorded.</p>
      )}

      <h4>Communication Observations</h4>
      {summary.communication_observations?.length ? (
        <ul>
          {summary.communication_observations.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">No communication observations recorded.</p>
      )}
    </section>
  );
}

export default function HRDashboard() {
  const {
    data: interviews,
    loading,
    error,
    reload,
  } = useFetch(() => api.listInterviews());

  const [busyId, setBusyId] = useState(null);
  const [actionError, setActionError] = useState("");

  const [reportId, setReportId] = useState(null);
  const [report, setReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState("");

  async function toggleCancel(interview) {
    setBusyId(interview.interview_id);
    setActionError("");

    try {
      await api.updateInterview(interview.interview_id, {
        status: interview.status === "open" ? "closed" : "open",
      });

      reload();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  async function toggleReport(interviewId) {
    if (reportId === interviewId) {
      setReportId(null);
      setReport(null);
      setReportError("");
      return;
    }

    setReportId(interviewId);
    setReport(null);
    setReportError("");
    setReportLoading(true);

    try {
      const result = await api.getInterviewReport(interviewId);
      setReport(result);
    } catch (err) {
      setReportError(err.message);
    } finally {
      setReportLoading(false);
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

      {loading && !interviews && (
        <p className="muted">Loading...</p>
      )}

      {interviews && interviews.length === 0 && (
        <p className="muted">
          You have not created any interviews yet. Click "Create interview" to
          assign one to a candidate.
        </p>
      )}

      <div className="list">
        {interviews?.map((interview) => (
          <article
            className="card item"
            key={interview.interview_id}
          >
            <div className="item-main">
              <h2>{interview.job_title}</h2>

              <div className="meta">
                <StatusBadge value={hrStatus(interview)} />

                {interview.has_report && (
                  <span className="status status-completed">
                    Report ready
                  </span>
                )}
              </div>

              {interview.candidate ? (
                <>
                  <p className="muted">
                    Candidate: {candidateLabel(interview.candidate)}
                  </p>

                  <p className="muted">
                    Scheduled: {formatDateTime(interview.scheduled_at)}
                  </p>
                </>
              ) : (
                <p className="muted">No candidate assigned</p>
              )}
            </div>

            <div className="actions">
              <Link
                className="btn btn-secondary"
                to={`/hr/interviews/${interview.interview_id}`}
              >
                View
              </Link>

              {interview.has_report && (
                <button
                  className="btn btn-secondary"
                  onClick={() => toggleReport(interview.interview_id)}
                >
                  {reportId === interview.interview_id
                    ? "Hide Report"
                    : "View Report"}
                </button>
              )}

                            {(interview.status === "open" ||
                interview.status === "closed") && (
                <button
                  className="btn btn-secondary"
                  disabled={busyId === interview.interview_id}
                  onClick={() => toggleCancel(interview)}
                >
                  {interview.status === "open"
                    ? "Cancel interview"
                    : "Reopen interview"}
                </button>
              )}
            </div>

            {reportId === interview.interview_id && (
              <div style={{ width: "100%" }}>
                {reportLoading && (
                  <p className="muted">Loading report...</p>
                )}

                {reportError && (
                  <p className="error">{reportError}</p>
                )}

                {report && (
                  <InterviewReport report={report} />
                )}
              </div>
            )}
          </article>
        ))}
      </div>
    </>
  );
}
