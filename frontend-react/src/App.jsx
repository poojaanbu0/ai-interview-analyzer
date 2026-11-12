import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { homeFor, useAuth } from "./AuthContext.jsx";
import Layout from "./components/Layout.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import HRDashboard from "./pages/HRDashboard.jsx";
import CreateInterview from "./pages/CreateInterview.jsx";
import EditInterview from "./pages/EditInterview.jsx";
import InterviewDetail from "./pages/InterviewDetail.jsx";
import MyInterviews from "./pages/MyInterviews.jsx";
import InterviewRoom from "./pages/InterviewRoom.jsx";

// Keeps a candidate out of HR pages (and the reverse) when they type the URL.
// This only hides the screens; the backend enforces the real permissions.
function RequireRole({ role }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== role) return <Navigate to={homeFor(user.role)} replace />;
  return <Outlet />;
}

function Home() {
  const { user } = useAuth();
  return <Navigate to={user ? homeFor(user.role) : "/login"} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<RequireRole role="hr" />}>
        <Route element={<Layout />}>
          <Route path="/hr" element={<HRDashboard />} />
          <Route path="/hr/interviews/new" element={<CreateInterview />} />
          <Route path="/hr/interviews/:id" element={<InterviewDetail />} />
          <Route path="/hr/interviews/:id/edit" element={<EditInterview />} />
        </Route>
      </Route>

      <Route element={<RequireRole role="candidate" />}>
        <Route element={<Layout />}>
          <Route path="/candidate" element={<MyInterviews />} />
          <Route path="/candidate/interview/:applicationId" element={<InterviewRoom />} />
        </Route>
      </Route>

      <Route path="*" element={<Home />} />
    </Routes>
  );
}