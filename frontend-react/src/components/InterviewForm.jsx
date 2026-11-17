import { useState } from "react";
import { Link } from "react-router-dom";
import { candidateLabel, fromInputValue, toInputValue } from "../utils.js";

const EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Internship", "Contract"];
const EXPERIENCE_LEVELS = ["Fresher", "1-3 years", "3-5 years", "5+ years"];

const clean = (value) => (value.trim() === "" ? null : value.trim());

// Used by both Create Interview and Edit Interview.
export default function InterviewForm({
  initial,
  candidates = [],
  lockedCandidate,
  submitLabel,
  busy,
  error,
  cancelTo,
  onSubmit,
}) {
  // InterviewOut contains these fields directly, not inside initial.assignment.
  const initialSchedule = initial?.scheduled_at
    ? toInputValue(initial.scheduled_at)
    : "";

  const [form, setForm] = useState({
    job_title: initial?.job_title ?? "",
    job_description: initial?.job_description ?? "",
    requirements: initial?.requirements ?? "",
    location: initial?.location ?? "",
    employment_type: initial?.employment_type ?? "",
    experience_level: initial?.experience_level ?? "",
    candidate_summary: initial?.candidate_summary ?? "",
    scheduled_at: initialSchedule,
  });

  const [candidateId, setCandidateId] = useState("");
  const [localError, setLocalError] = useState("");

  const update = (field) => (e) => {
    setForm((previous) => ({
      ...previous,
      [field]: e.target.value,
    }));
  };

  function handleSubmit(e) {
    e.preventDefault();
    setLocalError("");

    const payload = {
      job_title: form.job_title.trim(),
      job_description: form.job_description.trim(),
      requirements: clean(form.requirements),
      location: clean(form.location),
      employment_type: clean(form.employment_type),
      experience_level: clean(form.experience_level),
      candidate_summary: form.candidate_summary.trim(),
    };

    // Send the schedule only if it has changed.
    if (form.scheduled_at !== initialSchedule) {
      payload.scheduled_at = fromInputValue(form.scheduled_at);
    }

    // Candidate selection is required only when creating an interview.
    if (!lockedCandidate) {
      if (!candidateId) {
        setLocalError("Please select a candidate");
        return;
      }

      payload.candidate_id = Number(candidateId);
    }

    onSubmit(payload);
  }

  return (
    <form className="card form-grid" onSubmit={handleSubmit}>
      <h2 className="full">Candidate and schedule</h2>

      {lockedCandidate ? (
        <label className="full">
          Candidate
          <input value={lockedCandidate} disabled />
        </label>
      ) : (
        <label className="full">
          Select candidate
          <select
            value={candidateId}
            onChange={(e) => setCandidateId(e.target.value)}
            required
          >
            <option value="">-- Select a candidate --</option>

            {candidates.map((candidate) => (
              <option key={candidate.user_id} value={candidate.user_id}>
                {candidateLabel(candidate)}
              </option>
            ))}
          </select>
        </label>
      )}

      <label>
        Interview date and time
        <input
          type="datetime-local"
          value={form.scheduled_at}
          onChange={update("scheduled_at")}
          required
        />
        <span className="hint">
          The candidate can start only from this time. Shown in your local time
          zone.
        </span>
      </label>

      <label className="full">
        Candidate summary
        <textarea
          rows={5}
          value={form.candidate_summary}
          onChange={update("candidate_summary")}
          required
          placeholder="Summary of the candidate's resume: education, skills, projects, experience"
        />
        <span className="hint">
          Only HR can see this. The AI uses it to tailor the interview questions.
        </span>
      </label>

      <h2 className="full">Job details</h2>

      <label className="full">
        Job title
        <input
          value={form.job_title}
          onChange={update("job_title")}
          required
          maxLength={200}
        />
      </label>

      <label className="full">
        Job description
        <textarea
          rows={6}
          value={form.job_description}
          onChange={update("job_description")}
          required
        />
      </label>

      <label className="full">
        Requirements
        <textarea
          rows={4}
          value={form.requirements}
          onChange={update("requirements")}
        />
      </label>

      <label>
        Location
        <input
          value={form.location}
          onChange={update("location")}
          maxLength={150}
        />
      </label>

      <label>
        Employment type
        <select
          value={form.employment_type}
          onChange={update("employment_type")}
        >
          <option value="">Not specified</option>
          {EMPLOYMENT_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </label>

      <label>
        Experience level
        <select
          value={form.experience_level}
          onChange={update("experience_level")}
        >
          <option value="">Not specified</option>
          {EXPERIENCE_LEVELS.map((level) => (
            <option key={level} value={level}>
              {level}
            </option>
          ))}
        </select>
      </label>

      {(localError || error) && (
        <p className="error full">{localError || error}</p>
      )}

      <div className="full actions">
        <button className="btn" disabled={busy}>
          {busy ? "Saving..." : submitLabel}
        </button>

        <Link className="btn btn-secondary" to={cancelTo}>
          Cancel
        </Link>
      </div>
    </form>
  );
}
