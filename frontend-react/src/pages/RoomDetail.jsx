import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import { useFetch } from "../hooks.js";
import { formatDateTime } from "../utils.js";
import AssignCandidateModal from "../components/AssignCandidateModal.jsx";
import ViewToggle from "../components/ViewToggle.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

const STATUS_OPTIONS = [
  { value: "", label: "All statuses" },
  { value: "open", label: "Open" },
  { value: "in_progress", label: "In Progress" },
  { value: "completed", label: "Completed" },
  { value: "closed", label: "Cancelled" },
];

const SORT_OPTIONS = [
  { value: "date", label: "Date" },
  { value: "score", label: "Score (high→low)" },
  { value: "name", label: "Name" },
];

function ScoreBadge({ score }) {
  if (score == null) return null;
  const rounded = Math.round(score);
  let cls = "score-badge";
  if (rounded >= 75) cls += " score-high";
  else if (rounded >= 50) cls += " score-mid";
  else cls += " score-low";
  return <span className={cls}>{rounded}%</span>;
}

function ProgressBar({ completed, total }) {
  const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
  return (
    <div className="room-progress" style={{ marginBottom: "1.5rem" }}>
      <div className="room-progress-track">
        <div className="room-progress-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="room-progress-label">
        {completed}/{total} interviews completed
      </span>
    </div>
  );
}

export default function RoomDetail() {
  const { roomId } = useParams();
  const [showModal, setShowModal] = useState(false);
  const [view, setView] = useState("card");
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("date");

  const {
    data: roomResponse,
    loading,
    error,
    reload,
  } = useFetch(
    () => api.getRoom(roomId),
    [roomId]
  );

  const room = roomResponse?.room ?? roomResponse;
  const roomCandidates =
    roomResponse?.candidates ?? room?.candidates ?? [];

  if (loading && !roomResponse) return <p className="muted">Loading room...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!room) return null;

  // Client-side filter/sort on the candidates list
  let candidates = roomCandidates;

  if (statusFilter) {
    candidates = candidates.filter((c) => c.status === statusFilter);
  }
  if (search.trim()) {
    const q = search.toLowerCase();
    candidates = candidates.filter((c) =>
      c.candidate_name.toLowerCase().includes(q)
    );
  }
  if (sortBy === "score") {
    candidates = [...candidates].sort(
      (a, b) => (b.overall_score ?? -1) - (a.overall_score ?? -1)
    );
  } else if (sortBy === "name") {
    candidates = [...candidates].sort((a, b) =>
      a.candidate_name.localeCompare(b.candidate_name)
    );
  }

  const completedCount = roomCandidates.filter(
    (c) => c.status === "completed"
  ).length;

  return (
    <>
      <div className="page-title">
        <div>
          <Link to="/hr/rooms" className="back-link">← Back to Rooms</Link>
        </div>
        <button className="btn" onClick={() => setShowModal(true)}>
          Assign Candidate
        </button>
      </div>

      {/* Room info */}
      <section className="card" style={{ marginBottom: "1rem" }}>
        <h1>{room.job_title}</h1>
        <div className="detail-grid">
          <div className="kv">
            <dt>Location</dt>
            <dd>{room.location || "Not specified"}</dd>
          </div>
          <div className="kv">
            <dt>Employment Type</dt>
            <dd>{room.employment_type || "Not specified"}</dd>
          </div>
          <div className="kv">
            <dt>Experience Level</dt>
            <dd>{room.experience_level || "Not specified"}</dd>
          </div>
        </div>
        <h3>Job description</h3>
        <p className="text-block" style={{ fontSize: "0.9rem" }}>
          {room.job_description || "Not provided"}
        </p>
        <h3>Requirements</h3>
        <p className="text-block" style={{ fontSize: "0.9rem" }}>
          {room.requirements || "Not specified"}
        </p>
      </section>

      <ProgressBar
        completed={completedCount}
        total={roomCandidates.length}
      />

      {/* Filters */}
      <div className="filter-bar">
        <input
          className="filter-search"
          type="text"
          placeholder="Search candidate..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="filter-select"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <select
          className="filter-select"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <ViewToggle view={view} onToggle={setView} />
      </div>

      {candidates.length === 0 && (
        <p className="muted" style={{ marginTop: "1rem" }}>
          No candidates match the current filters.
        </p>
      )}

      {/* Card View */}
      {view === "card" && candidates.length > 0 && (
        <div className="candidates-grid">
          {candidates.map((c) => (
            <div key={c.interview_id} className="candidate-card">
              <div className="candidate-card-top">
                <h3>{c.candidate_name}</h3>
                <StatusBadge value={c.status} />
              </div>
              <p className="muted">{c.candidate_email}</p>
              <p className="muted">{formatDateTime(c.scheduled_at)}</p>
              {c.overall_score != null && (
                <div className="candidate-card-score">
                  <span className="muted">Score</span>
                  <ScoreBadge score={c.overall_score} />
                </div>
              )}
              {c.candidate_summary && (
                <p className="candidate-summary-preview">
                  {c.candidate_summary.slice(0, 120)}
                  {c.candidate_summary.length > 120 ? "..." : ""}
                </p>
              )}
              <div className="candidate-card-actions">
                {c.status === "completed" ? (
                  <Link
                    className="btn btn-sm"
                    to={`/hr/rooms/${roomId}/candidates/${c.interview_id}`}
                  >
                    View Result
                  </Link>
                ) : (
                  <Link
                    className="btn btn-secondary btn-sm"
                    to={`/hr/interviews/${c.interview_id}`}
                  >
                    View Details
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Table View */}
      {view === "table" && candidates.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Email</th>
                <th>Scheduled</th>
                <th>Status</th>
                <th>Score</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr key={c.interview_id}>
                  <td><strong>{c.candidate_name}</strong></td>
                  <td>{c.candidate_email}</td>
                  <td>{formatDateTime(c.scheduled_at)}</td>
                  <td><StatusBadge value={c.status} /></td>
                  <td><ScoreBadge score={c.overall_score} /></td>
                  <td>
                    {c.status === "completed" ? (
                      <Link
                        className="btn btn-sm"
                        to={`/hr/rooms/${roomId}/candidates/${c.interview_id}`}
                      >
                        Result
                      </Link>
                    ) : (
                      <Link
                        className="btn btn-secondary btn-sm"
                        to={`/hr/interviews/${c.interview_id}`}
                      >
                        Details
                      </Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <AssignCandidateModal
          roomId={roomId}
          onClose={() => setShowModal(false)}
          onAssigned={reload}
        />
      )}
    </>
  );
}
