import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import { useFetch } from "../hooks.js";
import { formatDateTime } from "../utils.js";
import ChatBubbles from "../components/ChatBubbles.jsx";

const METRIC_LABELS = {
  technical_strength: "Technical Strength",
  communication: "Communication",
  confidence: "Confidence",
  problem_solving: "Problem Solving",
  relevance: "Relevance",
  clarity: "Clarity",
};

const METRIC_COLORS = {
  technical_strength: "var(--color-accent-blue)",
  communication: "var(--color-teal-500)",
  confidence: "var(--tally-purple)",
  problem_solving: "var(--tally-yellow)",
  relevance: "var(--tally-green)",
  clarity: "var(--color-teal-700)",
};

function MetricBar({ name, value }) {
  const score = Math.max(0, Math.min(100, value ?? 0));
  return (
    <div className="result-metric">
      <div className="result-metric-header">
        <span>{METRIC_LABELS[name] || name}</span>
        <strong>{score}/100</strong>
      </div>
      <div className="result-metric-track">
        <div
          className="result-metric-fill"
          style={{
            width: `${score}%`,
            background: METRIC_COLORS[name] || "var(--color-teal-500)",
          }}
        />
      </div>
    </div>
  );
}

function OverallScore({ metrics }) {
  const keys = Object.keys(METRIC_LABELS);
  const scores = keys.map((k) => metrics[k] ?? 0);
  const avg = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);

  let cls = "overall-score";
  if (avg >= 75) cls += " score-high";
  else if (avg >= 50) cls += " score-mid";
  else cls += " score-low";

  return (
    <div className={cls}>
      <span className="overall-score-value">{avg}</span>
      <span className="overall-score-label">Overall Score</span>
    </div>
  );
}

export default function CandidateResult() {
  const { roomId, interviewId } = useParams();
  const [downloading, setDownloading] = useState(false);

  const { data: report, loading, error } = useFetch(
    () => api.getInterviewReport(interviewId),
    [interviewId]
  );

  const { data: interview } = useFetch(
    () => api.getInterview(interviewId),
    [interviewId]
  );

  async function handleDownloadPdf() {
    setDownloading(true);
    try {
      const blob = await api.downloadReportPdf(interviewId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `interview-report-${interviewId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Failed to download PDF");
    } finally {
      setDownloading(false);
    }
  }

  if (loading) return <p className="muted">Loading report...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!report) return null;

  const summary = report.report_data?.summary || {};
  const metrics = report.report_data?.metrics || {};

  return (
    <>
      <div className="page-title">
        <div>
          <Link to={`/hr/rooms/${roomId}`} className="back-link">
            ← Back to Room
          </Link>
          <h1>
            {interview?.candidate?.name || "Candidate"} — Interview Result
          </h1>
        </div>
        <button
          className="btn"
          onClick={handleDownloadPdf}
          disabled={downloading}
        >
          {downloading ? "Downloading..." : "Download PDF"}
        </button>
      </div>

      {/* Overall Score */}
      <div className="result-overview">
        <OverallScore metrics={metrics} />

        <div className="result-meta">
          {interview && (
            <>
              <p><strong>Job:</strong> {interview.job_title}</p>
              <p><strong>Scheduled:</strong> {formatDateTime(interview.scheduled_at)}</p>
            </>
          )}
          <p className="muted">
            Report generated: {formatDateTime(report.generated_at)}
          </p>
        </div>
      </div>

      {/* Metrics */}
      <section className="card result-metrics-card">
        <h3>Performance Metrics</h3>
        <div className="result-metrics-grid">
          {Object.keys(METRIC_LABELS).map((key) => (
            <MetricBar key={key} name={key} value={metrics[key]} />
          ))}
        </div>
      </section>

      {/* Summary */}
      <section className="card">
        <h3>Overall Summary</h3>
        <p className="text-block">
          {summary.overall_summary || "No summary available."}
        </p>

        {summary.key_strengths?.length > 0 && (
          <>
            <h4>Key Strengths</h4>
            <ul className="result-list result-list-green">
              {summary.key_strengths.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </>
        )}

        {summary.improvement_areas?.length > 0 && (
          <>
            <h4>Areas for Improvement</h4>
            <ul className="result-list result-list-yellow">
              {summary.improvement_areas.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </>
        )}

        {summary.technical_topics?.length > 0 && (
          <>
            <h4>Technical Topics Discussed</h4>
            <div className="chip-group">
              {summary.technical_topics.map((t, i) => (
                <span key={i} className="chip">{t}</span>
              ))}
            </div>
          </>
        )}
      </section>

      {/* Conversation — WhatsApp style */}
      <section className="card">
        <h3>Interview Conversation</h3>
        <ChatBubbles conversations={report.responses || []} />
      </section>
    </>
  );
}
