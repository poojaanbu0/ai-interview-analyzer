// One place for every call to the FastAPI backend.
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const getToken = () => localStorage.getItem("token");

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

function errorMessage(data, fallback) {
  if (!data || !data.detail) return fallback;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    // FastAPI validation errors (422): "email: value is not a valid email address"
    return data.detail
      .map((d) => `${(d.loc || []).slice(1).join(".")}: ${d.msg}`)
      .join("; ");
  }
  return fallback;
}

async function request(path, { method = "GET", json, body, auth = true } = {}) {
  const headers = {};
  let payload = body; // FormData / URLSearchParams are sent as they are

  if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(json);
  }
  const token = getToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${API_URL}${path}`, { method, headers, body: payload });
  } catch {
    throw new ApiError("Cannot reach the server. Is the backend running?", 0);
  }

  // token expired or invalid -> AuthContext logs the user out
  if (res.status === 401 && auth) window.dispatchEvent(new Event("auth:expired"));

  const data = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(errorMessage(data, res.statusText), res.status);
  return data;
}

export const api = {
  // ---- auth ----
  register: (data) => request("/auth/register", { method: "POST", json: data, auth: false }),
  // the login route takes form fields; the email goes in "username"
  login: (email, password) =>
    request("/auth/login", {
      method: "POST",
      auth: false,
      body: new URLSearchParams({ username: email, password }),
    }),
  me: () => request("/auth/me"),

  // ---- HR ----
  listInterviews: () => request("/interviews"),
  getInterview: (id) => request(`/interviews/${id}`),
  createInterview: (data) => request("/interviews", { method: "POST", json: data }),
  updateInterview: (id, data) => request(`/interviews/${id}`, { method: "PATCH", json: data }),
  listApplicants: (id) => request(`/interviews/${id}/applicants`),

  // ---- candidate ----
  browseJobs: (q) => request(`/jobs${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  applyToJob: (interviewId, file) => {
    const form = new FormData();
    form.append("interview_id", interviewId);
    form.append("resume", file);
    return request("/applications", { method: "POST", body: form });
  },
  myApplications: () => request("/applications/mine"),
  attendInterview: (applicationId) =>
    request(`/applications/${applicationId}/attend`, { method: "POST" }),
  finishInterview: (applicationId) =>
    request(`/applications/${applicationId}/finish`, { method: "POST" }),
};

// HR resume download: a plain <a href> can't send the token, so fetch it as a file.
export async function downloadResume(applicationId) {
  const res = await fetch(`${API_URL}/hr/applications/${applicationId}/resume`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (!res.ok) throw new ApiError("Could not download the resume", res.status);

  const disposition = res.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="?([^";]+)"?/);
  const filename = match ? match[1] : `resume_${applicationId}`;

  const url = URL.createObjectURL(await res.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}