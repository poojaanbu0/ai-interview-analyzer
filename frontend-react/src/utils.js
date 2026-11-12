export const formatDate = (iso) =>
  iso
    ? new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" })
    : "";

// The backend sends times in UTC ("...Z"); the browser shows them in the viewer's own time zone.
export const formatDateTime = (iso) =>
  iso
    ? new Date(iso).toLocaleString(undefined, {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
      })
    : "Not scheduled";

// "in_progress" -> "In progress"
export const label = (value) =>
  value ? value.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase()) : "";

// UTC ISO string -> value for <input type="datetime-local"> in the user's own time zone
export function toInputValue(iso) {
  const d = new Date(iso);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

// value of <input type="datetime-local"> (local time) -> UTC ISO string for the API
export const fromInputValue = (value) => new Date(value).toISOString();

export function formatCountdown(total) {
  const d = Math.floor(total / 86400);
  const h = Math.floor((total % 86400) / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m ${String(s).padStart(2, "0")}s`;
}

// What HR sees as the interview's status
export function hrStatus(interview) {
  if (interview.status === "closed") return "cancelled";
  const session = interview.assignment?.session_status;
  if (session === "completed" || session === "abandoned" || session === "in_progress") return session;
  return "scheduled";
}

// HR can edit or cancel only until the candidate has started
export const hasStarted = (interview) => Boolean(interview.assignment?.session_status);

export const candidateLabel = (c) => `${c.name} - ${c.candidate_code}`;