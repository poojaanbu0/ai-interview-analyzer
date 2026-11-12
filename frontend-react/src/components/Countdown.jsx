import { useEffect, useState } from "react";
import { formatCountdown } from "../utils.js";

// Counts down from `seconds` (given by the server) and calls onDone once at zero,
// so the page can ask the server again whether the interview can start.
export default function Countdown({ seconds, onDone }) {
  const [endAt] = useState(() => Date.now() + seconds * 1000);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

  const left = Math.max(0, Math.ceil((endAt - now) / 1000));

  useEffect(() => {
    if (left === 0) onDone();
  }, [left, onDone]);

  return <span>{formatCountdown(left)}</span>;
}