import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";
import Countdown from "../components/Countdown.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { useFetch } from "../hooks.js";
import { formatDateTime } from "../utils.js";

function InterviewCard({ item, onStartTimeReached }) {
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState(false);

  const buttonLabel =
    item.state === "in_progress" ? "Resume interview" : item.state === "ready" ? "Start interview" : "Attend interview";

  return (
    <article className="card">
      <div className="item">
        <div className="item-main">
          <h2>{item.job_title}</h2>
          <div className="meta">
            <StatusBadge value={item.state} />
            {item.location && <span className="chip">{item.location}</span>}
            {item.employment_type && <span className="chip">{item.employment_type}</span>}
            {item.experience_level && <span className="chip">{item.experience_level}</span>}
          </div>
          <p>
            <strong>Scheduled:</strong> {formatDateTime(item.scheduled_at)}
          </p>
        </div>

        <div className="actions action-col">
          {item.state === "completed" ? (
            <span className="muted">Interview completed</span>
          ) : (
            <>
              <button className="btn" disabled={!item.can_attend} onClick={() => navigate(`/candidate/interview/${item.application_id}`)}>
                {buttonLabel}
              </button>
              {item.state === "upcoming" && (
                <span className="muted">
                  Starts in{" "}
                  <Countdown
                    key={`${item.application_id}-${item.seconds_until_start}`}
                    seconds={item.seconds_until_start}
                    onDone={onStartTimeReached}
                  />
                </span>
              )}
            </>
          )}
          <button className="btn btn-secondary" onClick={() => setExpanded(!expanded)}>
            {expanded ? "Hide details" : "View details"}
          </button>
        </div>
      </div>

      {expanded && (
        <div>
          <h3>Job description</h3>
          <p className="text-block">{item.job_description}</p>
          {item.requirements && (
            <>
              <h3>Requirements</h3>
              <p className="text-block">{item.requirements}</p>
            </>
          )}
        </div>
      )}
    </article>
  );
}

export default function MyInterviews() {
  const { data: interviews, loading, error, reload } = useFetch(() => api.myInterviews());

  return (
    <>
      <div className="page-title">
        <h1>My interviews</h1>
      </div>

      {error && <p className="error">{error}</p>}
      {loading && !interviews && <p className="muted">Loading...</p>}
      {interviews && interviews.length === 0 && (
        <p className="muted">No interviews have been assigned to you yet. They will appear here once HR schedules one.</p>
      )}

      <div className="list">
        {interviews?.map((item) => (
          // when the countdown ends, ask the server again; it decides whether the button is enabled
          <InterviewCard key={item.application_id} item={item} onStartTimeReached={reload} />
        ))}
      </div>
    </>
  );
}