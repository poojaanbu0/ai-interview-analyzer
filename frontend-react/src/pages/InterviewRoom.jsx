
import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import { blobToWav } from "../audio.js";
import { useRecorder } from "../useRecorder.js";

const formatTime = (s) =>
  `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

export default function InterviewRoom() {
  const { interviewId: interviewIdParam } = useParams();
  const interviewId = Number(interviewIdParam);

  const recorder = useRecorder();
  const started = useRef(false);

  const [phase, setPhase] = useState("loading");
  const [progress, setProgress] = useState({
    answered: 0,
    total: 5,
    question: "",
  });

  const [responses, setResponses] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    async function init() {
      try {
        if (!Number.isSafeInteger(interviewId) || interviewId <= 0) {
          throw new Error(
            "Invalid interview ID. Please return to My Interviews and try again."
          );
        }

        await api.attendInterview(interviewId);

        const state = await api.interviewState(interviewId);

        setProgress({
          answered: state.answered,
          total: state.total_questions,
          question: state.current_question || "",
        });

        setResponses(state.responses || []);

        setPhase(state.finished ? "finished" : "ready");
      } catch (err) {
        setError(err.message);
        setPhase("failed");
      }
    }

    init();
  }, [interviewId]);

  async function handleStart() {
    setError("");

    try {
      await recorder.start();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleStop() {
    setPhase("processing");
    setError("");

    try {
      const raw = await recorder.stop();
      const wav = await blobToWav(raw);

      const result = await api.submitAnswer(interviewId, wav);

      // Refresh saved responses after successful submission.
      const state = await api.interviewState(interviewId);

      setResponses(state.responses || []);

      setProgress({
        answered: result.answered,
        total: result.total_questions,
        question: result.next_question || "",
      });

      if (result.finished) {
        setPhase("finished");
      } else {
        setPhase("ready");
      }
    } catch (err) {
      setError(err.message);
      setPhase("ready");
    }
  }

  if (phase === "loading") {
    return <p className="muted">Starting your interview...</p>;
  }

  if (phase === "failed") {
    return (
      <div className="card">
        <h1>Interview</h1>
        <p className="error">{error}</p>
        <Link to="/candidate">Back to my interviews</Link>
      </div>
    );
  }

  if (phase === "finished") {
    return (
      <div className="card thank-you">
        <h1>Thank you for attending the interview</h1>
        <p>
          Your responses have been submitted. The hiring team will review them
          and get in touch.
        </p>

        <Link className="btn" to="/candidate">
          Back to my interviews
        </Link>
      </div>
    );
  }

  const busy = phase === "processing";
  const percent = Math.round(
    (progress.answered / progress.total) * 100
  );

  return (
    <div className="card interview-room">
      <p className="muted">
        Question {progress.answered + 1} of {progress.total}
      </p>

      <div className="progress">
        <div
          className="progress-bar"
          style={{ width: `${percent}%` }}
        />
      </div>

      <h2 className="question">{progress.question}</h2>

      {busy ? (
        <p className="processing">
          <span className="spinner" /> Analysing your answer. This can take up
          to a minute...
        </p>
      ) : recorder.recording ? (
        <div className="actions">
          <span className="rec">
            <span className="rec-dot" /> Recording {formatTime(recorder.seconds)}
          </span>

          <button className="btn" onClick={handleStop}>
            Stop and submit
          </button>
        </div>
      ) : (
        <button className="btn" onClick={handleStart}>
          Start recording
        </button>
      )}

      {error && <p className="error">{error}</p>}

      <p className="muted">
        Speak clearly. When you stop, your answer is submitted automatically.
      </p>

      {/* Previous questions and answers */}
      {responses.length > 0 && (
        <section className="candidate-response-history">
          <h3>Your Previous Responses</h3>

          {responses.map((item) => (
            <article
              className="candidate-response-card"
              key={item.question_number}
            >
              <p className="candidate-response-number">
                Question {item.question_number}
              </p>

              <h4>{item.question}</h4>

              <p className="candidate-answer-label">
                Your Answer
              </p>

              <p className="candidate-answer-text">
                {item.answer || "No answer recorded."}
              </p>
            </article>
          ))}
        </section>
      )}
    </div>
  );
}
