import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";

const HR_LINKS = [
  { to: "/hr", label: "My jobs", end: true },
  { to: "/hr/jobs/new", label: "Create interview" },
];
const CANDIDATE_LINKS = [
  { to: "/candidate", label: "Browse jobs", end: true },
  { to: "/candidate/applications", label: "My applications" },
];

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
        <strong>Kyra NOVA Interviews</strong>
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