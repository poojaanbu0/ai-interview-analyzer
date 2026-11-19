import { Link } from "react-router-dom";
import { api } from "../api.js";
import { useFetch } from "../hooks.js";
import { formatDateTime } from "../utils.js";

function ProgressBar({ completed, total }) {
  const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
  return (
    <div className="room-progress">
      <div className="room-progress-track">
        <div className="room-progress-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="room-progress-label">
        {completed}/{total} completed
      </span>
    </div>
  );
}

export default function HRRooms() {
  const { data: rooms, loading, error } = useFetch(() => api.listRooms());

  return (
    <>
      <div className="page-title">
        <h1>Interview Rooms</h1>
        <Link className="btn" to="/hr/rooms/new">
          Create Room
        </Link>
      </div>

      {error && <p className="error">{error}</p>}
      {loading && !rooms && <p className="muted">Loading...</p>}
      {rooms && rooms.length === 0 && (
        <p className="muted">
          No interview rooms yet. Click "Create Room" to set up a new job interview.
        </p>
      )}

      <div className="rooms-grid">
        {rooms?.map((room) => (
          <Link
            key={room.id}
            to={`/hr/rooms/${room.id}`}
            className="room-card"
          >
            <div className="room-card-header">
              <h2>{room.job_title}</h2>
              <span className={`status status-${room.status}`}>
                {room.status}
              </span>
            </div>

            <div className="room-card-meta">
              {room.location && <span className="chip">{room.location}</span>}
              {room.employment_type && (
                <span className="chip">{room.employment_type}</span>
              )}
              {room.experience_level && (
                <span className="chip">{room.experience_level}</span>
              )}
            </div>

            <ProgressBar
              completed={room.completed_count}
              total={room.candidate_count}
            />

            <p className="muted" style={{ fontSize: "0.8rem", marginTop: "0.5rem" }}>
              Created {formatDateTime(room.created_at)}
            </p>
          </Link>
        ))}
      </div>
    </>
  );
}
