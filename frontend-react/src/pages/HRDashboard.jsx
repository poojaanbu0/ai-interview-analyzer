import Header from "../components/Header.jsx";
import { useAuth } from "../AuthContext.jsx";

export default function HRDashboard() {
  const { user } = useAuth();
  return (
    <>
      <Header />
      <main className="page">
        <h1>HR Dashboard</h1>
        <p>Welcome, {user.name}.</p>
        <p className="muted">Next: create interviews, view created jobs and applicants.</p>
      </main>
    </>
  );
}