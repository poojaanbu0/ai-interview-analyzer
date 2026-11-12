import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api.js";

const EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Internship", "Contract"];
const EXPERIENCE_LEVELS = ["Fresher", "1-3 years", "3-5 years", "5+ years"];

const EMPTY = {
  job_title: "",
  job_description: "",
  requirements: "",
  location: "",
  employment_type: "",
  experience_level: "",
};

export default function CreateInterview() {
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      // optional fields: send null instead of an empty string
      const payload = Object.fromEntries(
        Object.entries(form).map(([key, value]) => [key, value.trim() === "" ? null : value.trim()])
      );
      await api.createInterview(payload);
      navigate("/hr"); // the new job is open and visible to candidates straight away
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-title">
        <h1>Create interview</h1>
        <Link className="btn btn-secondary" to="/hr">
          Cancel
        </Link>
      </div>

      <form className="card form-grid" onSubmit={handleSubmit}>
        <label className="full">
          Job title
          <input value={form.job_title} onChange={update("job_title")} required maxLength={200} autoFocus />
        </label>

        <label className="full">
          Job description
          <textarea rows={6} value={form.job_description} onChange={update("job_description")} required />
        </label>

        <label className="full">
          Requirements
          <textarea rows={4} value={form.requirements} onChange={update("requirements")} />
        </label>

        <label>
          Location
          <input value={form.location} onChange={update("location")} maxLength={150} />
        </label>

        <label>
          Employment type
          <select value={form.employment_type} onChange={update("employment_type")}>
            <option value="">Not specified</option>
            {EMPLOYMENT_TYPES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </label>

        <label>
          Experience level
          <select value={form.experience_level} onChange={update("experience_level")}>
            <option value="">Not specified</option>
            {EXPERIENCE_LEVELS.map((l) => (
              <option key={l}>{l}</option>
            ))}
          </select>
        </label>

        {error && <p className="error full">{error}</p>}

        <div className="full">
          <button className="btn" disabled={busy}>
            {busy ? "Creating..." : "Create interview"}
          </button>
        </div>
      </form>
    </>
  );
}