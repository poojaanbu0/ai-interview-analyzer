import Header from "../components/Header.jsx";
import { useAuth } from "../AuthContext.jsx";

export default function CandidateDashboard() {
  const { user } = useAuth();
  return (
    <>
      <Header />
      <main className="page">
        <h1>Candidate Dashboard</h1>
        <p>Welcome, {user.name}.</p>
        <p className="muted">Next: browse jobs, apply with your resume, attend the interview.</p>
      </main>
    </>
  );
}