import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { adminListProblems, adminDeleteProblem } from "../../api/problems";
import { DiffBadge, Loading, EmptyState, Spinner } from "../../components/Shared";
import { useToast } from "../../context/ToastContext";

export default function AdminProblems() {
  const navigate = useNavigate();
  const toast = useToast();
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);

  const load = () => {
    setLoading(true);
    adminListProblems()
      .then(setProblems)
      .catch((e) => toast?.(e?.response?.data?.detail || "Failed to load problems", "error"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDelete = async (p) => {
    if (!window.confirm(`Delete "${p.title}"? This removes all its test cases and submissions.`)) {
      return;
    }
    setDeleting(p.id);
    try {
      await adminDeleteProblem(p.id);
      toast?.("Problem deleted", "success");
      setProblems((ps) => ps.filter((x) => x.id !== p.id));
    } catch (e) {
      toast?.(e?.response?.data?.detail || "Delete failed", "error");
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div className="page-wrap">
      <div className="flex justify-between items-center gap-4 flex-wrap fade-up">
        <div className="page-header">
          <h1 className="page-title">Manage Problems</h1>
          <p className="page-sub">Create, edit, and remove coding practice problems.</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate("/admin/problems/new")}>
          + New Problem
        </button>
      </div>

      {loading ? (
        <Loading />
      ) : problems.length === 0 ? (
        <EmptyState
          icon="🧩"
          title="No problems yet"
          sub="Create your first coding problem to get started."
          action={
            <button className="btn btn-primary" onClick={() => navigate("/admin/problems/new")}>
              + New Problem
            </button>
          }
        />
      ) : (
        <div className="flex flex-col gap-3 fade-up-1">
          {problems.map((p, i) => (
            <div
              key={p.id}
              className="glass-panel glass-hover flex items-center justify-between gap-4 px-5 py-4 fade-up"
              style={{ animationDelay: `${Math.min(i, 8) * 0.03}s` }}
            >
              <div className="flex items-center gap-3 min-w-0">
                {p.is_locked && (
                  <span className="shrink-0" title="Password protected">
                    🔒
                  </span>
                )}
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-head font-semibold text-white/90 truncate">{p.title}</span>
                    {!p.is_active && <span className="badge-gray shrink-0">Inactive</span>}
                  </div>
                  <div className="text-xs text-white/40 mt-0.5 truncate">
                    {p.topic?.name || "No topic"} · {p.test_cases.length} test case
                    {p.test_cases.length !== 1 ? "s" : ""}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <DiffBadge level={p.difficulty} />
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => navigate(`/admin/problems/${p.id}/edit`)}
                >
                  Edit
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => handleDelete(p)}
                  disabled={deleting === p.id}
                >
                  {deleting === p.id ? <Spinner sm /> : "Delete"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
