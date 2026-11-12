import { useEffect, useState } from "react";
import { api } from "../api.js";
import JobCard from "../components/JobCard.jsx";
import { useFetch } from "../hooks.js";

export default function CandidateDashboard() {
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");

  // wait until the candidate stops typing before asking the backend
  useEffect(() => {
    const timer = setTimeout(() => setQuery(search.trim()), 300);
    return () => clearTimeout(timer);
  }, [search]);

  const { data: jobs, loading, error } = useFetch(() => api.browseJobs(query), [query]);

  return (
    <>
      <div className="page-title">
        <h1>Browse jobs</h1>
        <input
          type="search"
          placeholder="Search by job title"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ minWidth: 260 }}
        />
      </div>

      {error && <p className="error">{error}</p>}
      {loading && !jobs && <p className="muted">Loading...</p>}
      {jobs && jobs.length === 0 && (
        <p className="muted">{query ? "No jobs match your search." : "No jobs are open right now. Please check back later."}</p>
      )}

      <div className="list">
        {jobs?.map((job) => (
          <JobCard key={job.interview_id} job={job} />
        ))}
      </div>
    </>
  );
}