import { useEffect, useRef, useState } from "react";
import { Modal, Spinner } from "./Shared";
import { adminSearchLeetcode, adminImportLeetcode } from "../api/problems";

export default function LeetCodeImportModal({ onClose, onImport }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [importingSlug, setImportingSlug] = useState(null);
  const [error, setError] = useState("");
  const debounceRef = useRef(null);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    setSearching(true);
    setError("");
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      try {
        const r = await adminSearchLeetcode(query.trim());
        setResults(r.results);
      } catch (e) {
        setError(e?.response?.data?.detail || "Search failed");
        setResults([]);
      } finally {
        setSearching(false);
      }
    }, 400);
    return () => clearTimeout(debounceRef.current);
  }, [query]);

  const handlePick = async (titleSlug) => {
    setImportingSlug(titleSlug);
    setError("");
    try {
      const draft = await adminImportLeetcode(titleSlug);
      onImport(draft);
    } catch (e) {
      setError(e?.response?.data?.detail || "Import failed");
    } finally {
      setImportingSlug(null);
    }
  };

  return (
    <Modal title="Import from LeetCode" onClose={onClose}>
      <div className="flex flex-col gap-4">
        <input
          autoFocus
          className="input"
          placeholder="Search by title or number, e.g. 'two sum' or 1"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        {error && <p className="text-sm text-rose-300">{error}</p>}

        {searching && (
          <div className="flex items-center gap-2 text-sm text-white/50">
            <Spinner sm /> Searching…
          </div>
        )}

        {!searching && query.trim() && results.length === 0 && !error && (
          <p className="text-sm text-white/30">No matches.</p>
        )}

        <div className="flex flex-col gap-2 max-h-[50vh] overflow-y-auto">
          {results.map((r) => (
            <button
              key={r.title_slug}
              type="button"
              onClick={() => handlePick(r.title_slug)}
              disabled={importingSlug !== null || r.paid_only}
              className="glass rounded-2xl p-3.5 flex items-center justify-between gap-3 text-left hover:bg-white/[0.06] transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <div className="min-w-0">
                <p className="text-sm font-medium text-white/85 truncate">
                  {r.question_frontend_id}. {r.title}
                  {r.paid_only && <span className="text-white/30"> (premium)</span>}
                </p>
                {r.topics.length > 0 && (
                  <p className="text-xs text-white/35 truncate mt-0.5">
                    {r.topics.slice(0, 4).join(", ")}
                  </p>
                )}
              </div>
              <div className="shrink-0 flex items-center gap-2">
                {r.difficulty && (
                  <span
                    className={
                      r.difficulty === "Easy"
                        ? "badge-easy"
                        : r.difficulty === "Medium"
                        ? "badge-medium"
                        : "badge-hard"
                    }
                  >
                    {r.difficulty}
                  </span>
                )}
                {importingSlug === r.title_slug && <Spinner sm />}
              </div>
            </button>
          ))}
        </div>
      </div>
    </Modal>
  );
}
