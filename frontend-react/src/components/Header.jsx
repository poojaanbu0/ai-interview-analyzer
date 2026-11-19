import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";

const HR_LINKS = [
  { to: "/hr/rooms", label: "Interview Rooms", end: false },
  { to: "/hr/interviews", label: "Legacy Interviews", end: true },
];
const CANDIDATE_LINKS = [{ to: "/candidate", label: "My interviews", end: true }];

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const links = user?.role === "hr" ? HR_LINKS : CANDIDATE_LINKS;

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="header">
      <div className="header-left">
        <strong>Aalam Interview Analyzer</strong>
        <nav className="nav">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
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
