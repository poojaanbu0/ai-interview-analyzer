import { label } from "../utils.js";

export default function StatusBadge({ value }) {
  if (!value) return null;
  return <span className={`status status-${value}`}>{label(value)}</span>;
}