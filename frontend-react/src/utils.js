export const formatDate = (iso) =>
  iso
    ? new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" })
    : "";

// "in_progress" -> "In progress"
export const label = (value) =>
  value ? value.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase()) : "";

const ALLOWED_RESUME_TYPES = [".pdf", ".doc", ".docx"];
const MAX_RESUME_MB = 5; // keep in sync with MAX_RESUME_MB on the backend

// returns an error message, or "" when the file is fine
export function validateResume(file) {
  const dot = file.name.lastIndexOf(".");
  const ext = dot === -1 ? "" : file.name.slice(dot).toLowerCase();
  if (!ALLOWED_RESUME_TYPES.includes(ext)) return "Resume must be a PDF, DOC or DOCX file";
  if (file.size > MAX_RESUME_MB * 1024 * 1024) return `Resume must be smaller than ${MAX_RESUME_MB} MB`;
  return "";
}