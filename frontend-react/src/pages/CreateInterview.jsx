import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";
import InterviewForm from "../components/InterviewForm.jsx";
import { useFetch } from "../hooks.js";

export default function CreateInterview() {
  const navigate = useNavigate();
  const candidates = useFetch(() => api.listCandidates());
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(payload) {
    setError("");
    setBusy(true);
    try {
      await api.createInterview(payload);
      navigate("/hr"); // the candidate sees it in their dashboard straight away
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-title">
        <h1>Create interview</h1>
      </div>

      {candidates.error && <p className="error">{candidates.error}</p>}
      {candidates.loading && !candidates.data && <p className="muted">Loading candidates...</p>}
      {candidates.data && candidates.data.length === 0 && (
        <p className="muted">No candidates have registered yet. Ask the candidate to register first.</p>
      )}

      {candidates.data && (
        <InterviewForm
          candidates={candidates.data}
          submitLabel="Assign interview"
          busy={busy}
          error={error}
          cancelTo="/hr"
          onSubmit={handleSubmit}
        />
      )}
    </>
  );
}