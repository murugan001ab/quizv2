import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import CodeEditor from "../../components/CodeEditor";
import MobileCodeToolbar from "../../components/MobileCodeToolbar";
import DiscussionRoom from "../../components/DiscussionRoom";
import { DiffBadge, Spinner } from "../../components/Shared";
import { useKeyboardOpen } from "../../hooks/useKeyboardOffset";
import { getProblem, unlockProblem, runCode, submitCode, saveCode } from "../../api/problems";

export default function ProblemSolve() {
  const { id } = useParams();
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [unlockError, setUnlockError] = useState("");
  const [busy, setBusy] = useState(false);
  const [saveStatus, setSaveStatus] = useState("idle"); // idle | saving | saved | error
  const [result, setResult] = useState(null); // run result or submit result
  const [tab, setTab] = useState("description");
  // Mobile only: the split view collapses to one column at a time, this
  // picks which. Desktop (lg:+) always shows both side by side.
  const [mobileView, setMobileView] = useState("problem");
  const editorRef = useRef(null);
  // Only reserve room for the floating extra-keys toolbar while the on-screen
  // keyboard is actually open — otherwise that space just sits there empty.
  const keyboardOpen = useKeyboardOpen();

  const load = () => {
    getProblem(id).then((p) => {
      setProblem(p);
      setCode(p.saved_code || p.starter_code || "# write your solution here\n");
    });
  };

  useEffect(() => {
    setProblem(null);
    setCode("");
    setResult(null);
    setTab("description");
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleUnlock = async () => {
    setUnlockError("");
    try {
      await unlockProblem(id, password);
      load();
    } catch (e) {
      setUnlockError(e?.response?.data?.detail || "Incorrect password");
    }
  };

  const handleRun = async () => {
    setBusy(true);
    setResult(null);
    setTab("results");
    setMobileView("problem");
    try {
      const r = await runCode(id, code);
      setResult({ kind: "run", ...r });
    } finally {
      setBusy(false);
    }
  };

  const handleSave = async () => {
    setSaveStatus("saving");
    try {
      await saveCode(id, code);
      setSaveStatus("saved");
      setTimeout(() => setSaveStatus((s) => (s === "saved" ? "idle" : s)), 1800);
    } catch {
      setSaveStatus("error");
      setTimeout(() => setSaveStatus((s) => (s === "error" ? "idle" : s)), 2200);
    }
  };

  const handleSubmit = async () => {
    setBusy(true);
    setResult(null);
    setTab("results");
    setMobileView("problem");
    try {
      const r = await submitCode(id, code);
      setResult({ kind: "submit", ...r });
      if (r.status === "accepted") {
        setProblem((p) => (p ? { ...p, solved: true } : p));
      }
    } finally {
      setBusy(false);
    }
  };

  if (!problem) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (problem.is_locked) {
    return (
      <div className="auth-page">
        <div className="auth-bg" />
        <div className="auth-card fade-up">
          <div className="text-4xl text-center mb-3">🔒</div>
          <h2 className="font-head font-bold text-lg text-white text-center">{problem.title}</h2>
          <p className="auth-subtitle">This problem is password protected.</p>
          <div className="input-group mb-3">
            <input
              type="password"
              className="input"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleUnlock()}
            />
          </div>
          {unlockError && <p className="auth-error">{unlockError}</p>}
          <button onClick={handleUnlock} className="btn btn-primary w-full">
            Unlock
          </button>
          <Link to="/problems" className="auth-switch block">
            ← Back to problems
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Top bar */}
      <header className="flex items-center justify-between px-3 sm:px-5 py-3 sm:py-3.5 border-b border-white/10 glass shrink-0 z-10 gap-3">
        <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
          <Link to="/problems" className="btn btn-ghost btn-icon shrink-0" title="Back to problems">
            ←
          </Link>
          <div className={`min-w-0 `}>
            <h1 className="font-head font-bold text-white/90 truncate leading-tight text-sm sm:text-base">
              {problem.title}
            </h1>
            <div className="flex items-center gap-2 mt-1 flex-wrap">
              <DiffBadge level={problem.difficulty} />
              {problem.solved && <span className="badge-easy">Solved</span>}
              {/* {problem.topic?.name && <span className="tag">{problem.topic.name}</span>} */}
            </div>
          </div>
        </div>
      </header>

      {/* Mobile only: switch between the problem panel and the editor —
          there isn't room to show both side by side below lg. */}
      <div className="lg:hidden flex gap-1.5 px-3 pt-3 shrink-0">
        {[
          { key: "problem", label: "Problem" },
          { key: "code", label: "Code" },
        ].map((v) => (
          <button
            key={v.key}
            onClick={() => setMobileView(v.key)}
            className={`flex-1 py-2 rounded-2xl text-sm font-medium transition-all duration-200
              ${mobileView === v.key
                ? "bg-white/[0.09] text-white border border-white/10 shadow-inner-glass"
                : "text-white/40 border border-transparent"}`}
          >
            {v.label}
          </button>
        ))}
      </div>

      {/* Mobile only, code view only: Run/Submit right under the tabs so
          they're reachable the instant you're done typing — no need to
          scroll (or fight the on-screen keyboard) to reach them at the
          bottom of the editor. */}
      {mobileView === "code" && (
        <div className="lg:hidden flex items-center gap-2 px-3 pt-3 shrink-0">
          <button
            onClick={() => setCode(problem.starter_code || "")}
            className="btn btn-ghost btn-icon shrink-0"
            title="Reset to starter code"
          >
            ↺
          </button>
          <button
            onClick={handleSave}
            disabled={saveStatus === "saving"}
            className="btn btn-ghost btn-icon shrink-0"
            title="Save code"
          >
            {saveStatus === "saving" ? <Spinner sm /> : saveStatus === "saved" ? "✓" : "💾"}
          </button>
          <button onClick={handleRun} disabled={busy} className="btn btn-ghost flex-1">
            {busy ? <Spinner sm /> : "▶"} Run
          </button>
          <button onClick={handleSubmit} disabled={busy} className="btn btn-primary flex-1">
            {busy ? <Spinner sm /> : "✓"} Submit
          </button>
        </div>
      )}

      {/* Main split view */}
      <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 p-3 sm:p-4">
        {/* Left: description / test cases / results */}
        <div className={`glass-panel flex-col min-h-0 overflow-hidden ${mobileView === "problem" ? "flex" : "hidden"} lg:flex`}>
          <div className="flex gap-1.5 px-4 pt-4 shrink-0 overflow-x-auto">
            {[
              "description",
              "testcases",
              "results",
              ...(problem.solved ? ["discussion"] : []),
            ].map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-3.5 py-2 rounded-2xl text-sm font-medium capitalize transition-all duration-200 shrink-0
                  ${tab === t
                    ? "bg-white/[0.09] text-white border border-white/10 shadow-inner-glass"
                    : "text-white/40 hover:text-white/70 border border-transparent"}`}
              >
                {t}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-6 pt-4">
            {tab === "description" && (
              <div>
                <p className="whitespace-pre-wrap select-none text-sm leading-relaxed text-white/70">
                  {problem.description}
                </p>
                {problem.constraints && (
                  <>
                    <h3 className="font-head font-semibold mt-6 mb-2 text-sm text-white/80">
                      Constraints
                    </h3>
                    <p className="whitespace-pre-wrap text-sm text-white/50">
                      {problem.constraints}
                    </p>
                  </>
                )}
              </div>
            )}

            {tab === "testcases" && (
              <div className="space-y-4">
                {problem.visible_test_cases.map((tc, i) => (
                  <div key={i} className="glass rounded-2xl p-4 text-sm">
                    <p className="font-head font-semibold mb-2 text-white/80">Sample {i + 1}</p>
                    <p className="text-white/40 text-xs mb-1 uppercase tracking-wide">Input</p>
                    <pre className="bg-black/25 rounded-xl p-3 mb-3 whitespace-pre-wrap font-mono text-xs text-white/70">
                      {tc.input}
                    </pre>
                    <p className="text-white/40 text-xs mb-1 uppercase tracking-wide">
                      Expected Output
                    </p>
                    <pre className="bg-black/25 rounded-xl p-3 whitespace-pre-wrap font-mono text-xs text-white/70">
                      {tc.expected_output}
                    </pre>
                  </div>
                ))}
                <p className="text-xs text-white/30">
                  Additional hidden test cases are checked on Submit.
                </p>
              </div>
            )}

            {tab === "results" && <ResultsPanel result={result} busy={busy} />}

            {tab === "discussion" && problem.solved && <DiscussionRoom problemId={problem.id} />}
          </div>
        </div>

        {/* Right: editor + actions */}
        <div className={`flex-col min-h-0 gap-3 ${mobileView === "code" ? "flex" : "hidden"} lg:flex`}>
          <div className={`flex-1 min-h-0 ${keyboardOpen ? "pb-24" : ""}`}>
            <CodeEditor ref={editorRef} value={code} onChange={setCode} />
          </div>

          <MobileCodeToolbar editorRef={editorRef} />

          {/* Desktop only — mobile gets the compact bar under the tabs above */}
          <div className="hidden lg:flex glass-panel px-4 py-3 items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setCode(problem.starter_code || "")}
                className="btn btn-ghost btn-sm"
                title="Reset to starter code"
              >
                ↺ Reset
              </button>
              {saveStatus === "saved" && (
                <span className="text-xs text-emerald-300">Saved</span>
              )}
              {saveStatus === "error" && (
                <span className="text-xs text-rose-300">Save failed</span>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={saveStatus === "saving"}
                className="btn btn-ghost"
                title="Save code"
              >
                {saveStatus === "saving" ? <Spinner sm /> : "💾"} Save
              </button>
              <button onClick={handleRun} disabled={busy} className="btn btn-ghost">
                {busy ? <Spinner sm /> : "▶"} Run
              </button>
              <button onClick={handleSubmit} disabled={busy} className="btn btn-primary">
                {busy ? <Spinner sm /> : "✓"} Submit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ResultsPanel({ result, busy }) {
  if (busy) {
    return (
      <div className="flex items-center gap-3 text-sm text-white/50">
        <Spinner sm /> Judging your code…
      </div>
    );
  }
  if (!result) {
    return <p className="text-sm text-white/30">Run or submit to see results here.</p>;
  }

  const cases = result.results || [];
  const passedCount = cases.filter((c) => c.passed).length;
  const accepted = result.status === "accepted";

  return (
    <div>
      <div className="flex items-center gap-2.5 mb-5 flex-wrap">
        <span className={accepted ? "badge-easy" : "badge-hard"}>
          {result.status.replace(/_/g, " ")}
        </span>
        <span className="text-sm text-white/50">
          {passedCount}/{cases.length} passed
          {result.kind === "submit" && result.score !== undefined
            ? ` · score ${result.score}/${result.max_score}`
            : ""}
        </span>
      </div>

      <div className="space-y-3">
        {cases.map((c, i) => (
          <div
            key={i}
            className={`glass rounded-2xl p-4 text-sm border ${
              c.passed ? "border-emerald-400/25" : "border-rose-400/25"
            }`}
          >
            <p className="font-medium mb-2 text-white/80">
              {c.is_hidden ? `Hidden test ${i + 1}` : `Test ${i + 1}`} —{" "}
              {c.passed ? "✅ Passed" : "❌ Failed"}
            </p>
            {!c.is_hidden && (
              <>
                <p className="text-white/40 text-xs mb-1 uppercase tracking-wide">Your Output</p>
                <pre className="bg-black/25 rounded-xl p-3 mb-2 whitespace-pre-wrap font-mono text-xs text-white/70">
                  {c.stdout}
                </pre>
                {!c.passed && (
                  <>
                    <p className="text-white/40 text-xs mb-1 uppercase tracking-wide">Expected</p>
                    <pre className="bg-black/25 rounded-xl p-3 whitespace-pre-wrap font-mono text-xs text-white/70">
                      {c.expected}
                    </pre>
                  </>
                )}
                {c.stderr && (
                  <pre className="bg-rose-500/10 text-rose-300 rounded-xl p-3 mt-2 whitespace-pre-wrap font-mono text-xs">
                    {c.stderr}
                  </pre>
                )}
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
