import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="header">
      <strong>Kyra NOVA Interviews</strong>
      <div className="header-right">
        <span>{user?.name}</span>
        <span className="badge">{user?.role === "hr" ? "HR" : "Candidate"}</span>
        <button className="btn btn-secondary" onClick={handleLogout}>
          Log out
        </button>
      </div>
    </header>
  );
}