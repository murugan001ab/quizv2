import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listProblems, getTopics } from "../../api/problems";
import { DiffBadge, Loading, EmptyState } from "../../components/Shared";

export default function ProblemList() {
  const [problems, setProblems] = useState([]);
  const [topics, setTopics] = useState([]);
  const [topicId, setTopicId] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [solvedFilter, setSolvedFilter] = useState(""); // "" | "solved" | "unsolved"
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getTopics().then(setTopics).catch(() => { });
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (topicId) params.topic_id = topicId;
    if (difficulty) params.difficulty = difficulty;
    listProblems(params)
      .then(setProblems)
      .finally(() => setLoading(false));
  }, [topicId, difficulty]);

  const solvedCount = problems.filter((p) => p.solved).length;
  const visibleProblems = problems.filter((p) => {
    if (solvedFilter === "solved") return p.solved;
    if (solvedFilter === "unsolved") return !p.solved;
    return true;
  });

  return (
    <div className="page-wrap">
      <div className="page-header fade-up">
        <h1 className="page-title">Practice Problems</h1>
        <p className="page-sub">
          Sharpen your skills — solve, run, and submit right in the browser.
          {problems.length > 0 && (
            <span className="text-white/30"> · {solvedCount}/{problems.length} solved</span>
          )}
        </p>
      </div>

      <div className="flex gap-3 flex-wrap fade-up-1">
        <select
          className="input w-auto"
          value={topicId}
          onChange={(e) => setTopicId(e.target.value)}
        >
          <option value="">All Topics</option>
          {topics.map((t) => (
            <option key={t.id} value={t.id} className="bg-space-900">
              {t.name}
            </option>
          ))}
        </select>

        <select
          className="input w-auto"
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
        >
          <option value="">All Difficulties</option>
          <option value="basic" className="bg-space-900">Basic</option>
          <option value="intermediate" className="bg-space-900">Intermediate</option>
          <option value="advanced" className="bg-space-900">Advanced</option>
        </select>

        <select
          className="input w-auto"
          value={solvedFilter}
          onChange={(e) => setSolvedFilter(e.target.value)}
        >
          <option value="">All Problems</option>
          <option value="solved" className="bg-space-900">Solved</option>
          <option value="unsolved" className="bg-space-900">Not solved</option>
        </select>
      </div>

      {loading ? (
        <Loading />
      ) : visibleProblems.length === 0 ? (
        <EmptyState
          icon="🧩"
          title="No problems found"
          sub="Try a different topic, difficulty, or solved filter."
        />
      ) : (
        <div className="flex flex-col gap-3 fade-up-2">
          {visibleProblems.map((p, index) => (
            <button
              key={p.id}
              onClick={() => navigate(`/problems/${p.id}`)}
              className={`glass-panel glass-hover w-full flex items-center justify-between gap-4 px-5 py-4 text-left transition-all ${p.solved ? "border border-emerald-400/20 bg-emerald-500/5" : ""
                }`}
            >
              {/* Left Section: Index, Status Icon, Lock, Title */}
              <div className="flex items-center gap-3.5 min-w-0 flex-1">
                <span className="text-xs font-mono text-white/40 w-6 shrink-0">
                  {String(index + 1).padStart(2, "0")}
                </span>

                {p.solved ? (
                  <span className="shrink-0 text-emerald-400 text-sm" title="Solved">
                    ✓
                  </span>
                ) : (
                  <span
                    className="shrink-0 w-3.5 h-3.5 rounded-full border border-white/20"
                    title="Not solved yet"
                  />
                )}

                {p.is_locked && (
                  <span className="shrink-0 text-sm" title="Password protected">
                    🔒
                  </span>
                )}

                <span className="font-head font-medium text-white/90 truncate">
                  {p.title}
                </span>
              </div>

              {/* Right Section: Badges */}
              <div className="flex items-center gap-2 shrink-0">
                {p.solved && <span className="badge-easy">Solved</span>}
                <DiffBadge level={p.difficulty} />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
