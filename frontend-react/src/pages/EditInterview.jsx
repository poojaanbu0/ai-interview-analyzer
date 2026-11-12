import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api.js";
import InterviewForm from "../components/InterviewForm.jsx";
import { useFetch } from "../hooks.js";
import { candidateLabel, hasStarted } from "../utils.js";

export default function EditInterview() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: interview, error: loadError } = useFetch(() => api.getInterview(id), [id]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(payload) {
    setError("");
    setBusy(true);
    try {
      await api.updateInterview(id, payload);
      navigate(`/hr/interviews/${id}`);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  if (loadError) {
    return (
      <>
        <p className="error">{loadError}</p>
        <Link to="/hr">Back to my interviews</Link>
      </>
    );
  }
  if (!interview) return <p className="muted">Loading...</p>;

  if (hasStarted(interview)) {
    return (
      <>
        <p className="error">The candidate has already started this interview, so it can no longer be edited.</p>
        <Link to={`/hr/interviews/${id}`}>Back to the interview</Link>
      </>
    );
  }

  return (
    <>
      <div className="page-title">
        <h1>Edit interview</h1>
      </div>
      <InterviewForm
        initial={interview}
        lockedCandidate={interview.assignment ? candidateLabel(interview.assignment.candidate) : "No candidate"}
        submitLabel="Save changes"
        busy={busy}
        error={error}
        cancelTo={`/hr/interviews/${id}`}
        onSubmit={handleSubmit}
      />
    </>
  );
}