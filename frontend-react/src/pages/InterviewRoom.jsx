import { Link, useParams } from "react-router-dom";

// Placeholder: the AI interview room is built in the next step.
export default function InterviewRoom() {
  const { applicationId } = useParams();
  return (
    <div className="card">
      <h1>Interview room</h1>
      <p className="muted">The interview for application #{applicationId} will run here.</p>
      <Link to="/candidate/applications">Back to my applications</Link>
    </div>
  );
}