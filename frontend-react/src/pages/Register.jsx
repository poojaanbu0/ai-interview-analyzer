import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { api } from "../api.js";
import { homeFor, useAuth } from "../AuthContext.jsx";

export default function Register() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", phone: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to={homeFor(user.role)} replace />;

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await api.register({ ...form, name: form.name.trim(), email: form.email.trim(), phone: form.phone.trim() });
      const loggedIn = await login(form.email.trim(), form.password); // sign in straight away
      navigate(homeFor(loggedIn.role), { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <h1>Candidate registration</h1>

        <label>
          Full name
          <input value={form.name} onChange={update("name")} required maxLength={100} autoFocus />
        </label>

        <label>
          Email
          <input type="email" value={form.email} onChange={update("email")} required />
        </label>

        <label>
          Phone number
          <input type="tel" value={form.phone} onChange={update("phone")} required placeholder="10-digit mobile number" />
        </label>

        <label>
          Password (8 to 72 characters)
          <input type="password" value={form.password} onChange={update("password")} required minLength={8} maxLength={72} />
        </label>

        {error && <p className="error">{error}</p>}

        <button className="btn" disabled={busy}>
          {busy ? "Creating account..." : "Register"}
        </button>

        <p className="muted">
          Already registered? <Link to="/login">Log in</Link>
        </p>
        <p className="muted">HR accounts are created by the administrator.</p>
      </form>
    </div>
  );
}