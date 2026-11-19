import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api.js";

const EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Internship", "Contract"];
const EXPERIENCE_LEVELS = ["Fresher", "1-3 years", "3-5 years", "5+ years"];

export default function CreateRoom() {
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    job_title: "",
    job_description: "",
    requirements: "",
    location: "",
    employment_type: "",
    experience_level: "",
  });

  const update = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);

    const payload = {
      job_title: form.job_title.trim(),
      job_description: form.job_description.trim(),
      requirements: form.requirements.trim() || null,
      location: form.location.trim() || null,
      employment_type: form.employment_type || null,
      experience_level: form.experience_level || null,
    };

    try {
      const room = await api.createRoom(payload);
      navigate(`/hr/rooms/${room.id}`);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-title">
        <h1>Create Interview Room</h1>
      </div>

      <form className="card form-grid" onSubmit={handleSubmit}>
        <h2 className="full">Job Details</h2>

        <label className="full">
          Job Title
          <input
            value={form.job_title}
            onChange={update("job_title")}
            required
            maxLength={200}
            placeholder="e.g. Frontend Developer"
          />
        </label>

        <label className="full">
          Job Description
          <textarea
            rows={6}
            value={form.job_description}
            onChange={update("job_description")}
            required
            placeholder="Describe the role, responsibilities, and what you're looking for..."
          />
        </label>

        <label className="full">
          Requirements
          <textarea
            rows={4}
            value={form.requirements}
            onChange={update("requirements")}
            placeholder="Skills, qualifications, certifications..."
          />
        </label>

        <label>
          Location
          <input
            value={form.location}
            onChange={update("location")}
            maxLength={150}
            placeholder="e.g. Remote, Bangalore"
          />
        </label>

        <label>
          Employment Type
          <select value={form.employment_type} onChange={update("employment_type")}>
            <option value="">Not specified</option>
            {EMPLOYMENT_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </label>

        <label>
          Experience Level
          <select value={form.experience_level} onChange={update("experience_level")}>
            <option value="">Not specified</option>
            {EXPERIENCE_LEVELS.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </label>

        {error && <p className="error full">{error}</p>}

        <div className="full actions">
          <button className="btn" disabled={busy}>
            {busy ? "Creating..." : "Create Room"}
          </button>
          <Link className="btn btn-secondary" to="/hr/rooms">Cancel</Link>
        </div>
      </form>
    </>
  );
}
