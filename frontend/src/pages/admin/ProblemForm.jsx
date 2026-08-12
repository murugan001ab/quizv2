import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import {
  adminListTopics,
  adminCreateTopic,
  adminCreateProblem,
  adminGetProblem,
  adminUpdateProblem,
  adminAddTestCase,
  adminUpdateTestCase,
  adminDeleteTestCase,
} from "../../api/problems";
import { Loading, Spinner } from "../../components/Shared";
import LeetCodeImportModal from "../../components/LeetCodeImportModal";
import { useToast } from "../../context/ToastContext";

const emptyTestCase = () => ({
  id: null,
  input: "",
  expected_output: "",
  is_hidden: false,
  points: 1,
});

const emptyForm = {
  title: "",
  slug: "",
  description: "",
  constraints: "",
  starter_code: "",
  difficulty: "basic",
  topic_id: "",
  access_password: "",
  time_limit_ms: 2000,
  memory_limit_kb: 65536,
  allowed_languages: [],
  default_language: "",
};

const ALL_LANGUAGES = [
  { value: "python3", label: "Python 3" },
  { value: "java", label: "Java" },
  { value: "c", label: "C" },
];

export default function ProblemForm() {
  const { id } = useParams(); // present when editing
  const navigate = useNavigate();
  const toast = useToast();
  const isEdit = Boolean(id);

  const [topics, setTopics] = useState([]);
  const [newTopicName, setNewTopicName] = useState("");
  const [loading, setLoading] = useState(isEdit);

  const [form, setForm] = useState(emptyForm);
  const [testCases, setTestCases] = useState([emptyTestCase(), emptyTestCase(), emptyTestCase()]);
  const [saving, setSaving] = useState(false);
  const [clearPassword, setClearPassword] = useState(false);
  const [showLeetCodeModal, setShowLeetCodeModal] = useState(false);

  useEffect(() => {
    adminListTopics().then(setTopics).catch(() => {});
    if (isEdit) {
      setLoading(true);
      adminGetProblem(id)
        .then((p) => {
          setForm({
            title: p.title,
            slug: p.slug,
            description: p.description,
            constraints: p.constraints || "",
            starter_code: p.starter_code || "",
            difficulty: p.difficulty,
            topic_id: p.topic.id,
            access_password: "",
            time_limit_ms: p.time_limit_ms,
            memory_limit_kb: p.memory_limit_kb,
            allowed_languages: p.allowed_languages || [],
            default_language: p.default_language || "",
          });
          setTestCases(
            p.test_cases.length
              ? p.test_cases.map((tc) => ({ ...tc }))
              : [emptyTestCase(), emptyTestCase(), emptyTestCase()]
          );
        })
        .catch(() => toast?.("Failed to load problem", "error"))
        .finally(() => setLoading(false));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const updateField = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const toggleLanguage = (lang) =>
    setForm((f) => {
      const next = f.allowed_languages.includes(lang)
        ? f.allowed_languages.filter((l) => l !== lang)
        : [...f.allowed_languages, lang];
      // If the default language just got unchecked, clear it so we don't
      // submit a default that isn't in the allowed set.
      const default_language = next.includes(f.default_language) ? f.default_language : "";
      return { ...f, allowed_languages: next, default_language };
    });

  const updateTestCase = (i, k, v) =>
    setTestCases((tcs) => tcs.map((tc, idx) => (idx === i ? { ...tc, [k]: v } : tc)));

  const addTestCase = () => setTestCases((tcs) => [...tcs, emptyTestCase()]);

  const removeTestCase = async (i) => {
    const tc = testCases[i];
    if (isEdit && tc.id) {
      try {
        await adminDeleteTestCase(tc.id);
      } catch (e) {
        toast?.(e?.response?.data?.detail || "Failed to remove test case", "error");
        return;
      }
    }
    setTestCases((tcs) => tcs.filter((_, idx) => idx !== i));
  };

  const handleCreateTopic = async () => {
    if (!newTopicName.trim()) return;
    const slug = newTopicName.trim().toLowerCase().replace(/\s+/g, "-");
    try {
      const t = await adminCreateTopic({ name: newTopicName.trim(), slug, order_index: topics.length });
      setTopics((ts) => [...ts, t]);
      updateField("topic_id", t.id);
      setNewTopicName("");
      toast?.(`Topic "${t.name}" added`, "success");
    } catch (e) {
      toast?.(e?.response?.data?.detail || "Failed to create topic", "error");
    }
  };

  const handleImport = (draft) => {
    // Prefer a python3 snippet as the single starter_code field (the form
    // only has one slot); fall back to whatever LeetCode gave us.
    const starter =
      draft.starter_codes.find((s) => s.language === "python3") || draft.starter_codes[0];
    const availableLangs = draft.starter_codes.map((s) => s.language);

    setForm((f) => ({
      ...f,
      title: draft.title,
      slug: draft.slug,
      description: draft.description,
      constraints: draft.constraints || "",
      starter_code: starter ? starter.code : f.starter_code,
      difficulty: draft.difficulty,
      // Only restrict to what LeetCode actually gave us starter code for —
      // leave unchecked (all languages open) if we couldn't tell.
      allowed_languages: availableLangs.length ? availableLangs : [],
      default_language: starter ? starter.language : "",
    }));

    if (draft.examples.length) {
      setTestCases(
        draft.examples.map((ex, i) => ({
          id: null,
          input: ex.input,
          expected_output: ex.output,
          is_hidden: i >= 2, // keep the first couple visible, rest hidden
          points: 1,
        }))
      );
    }

    setShowLeetCodeModal(false);
    toast?.(
      draft.examples.length
        ? `Imported "${draft.title}" — double-check the ${draft.examples.length} example test case(s), LeetCode's I/O format doesn't always match stdin/stdout.`
        : `Imported "${draft.title}" — no example test cases could be parsed, add them manually.`,
      "success"
    );
  };

  const handleSave = async () => {
    if (!form.title.trim()) return toast?.("Title is required", "error");
    if (!form.slug.trim()) return toast?.("Slug is required", "error");
    if (!form.topic_id) return toast?.("Pick a topic", "error");
    if (!form.description.trim()) return toast?.("Description is required", "error");

    setSaving(true);
    try {
      const payload = { ...form, topic_id: Number(form.topic_id) };
      if (!payload.access_password) delete payload.access_password;
      payload.default_language = payload.default_language || null;

      if (isEdit) {
        await adminUpdateProblem(id, { ...payload, clear_password: clearPassword });
        for (const tc of testCases) {
          const body = {
            input: tc.input,
            expected_output: tc.expected_output,
            is_hidden: tc.is_hidden,
            points: tc.points,
          };
          if (tc.id) await adminUpdateTestCase(tc.id, body);
          else await adminAddTestCase(id, body);
        }
        toast?.("Problem updated", "success");
      } else {
        payload.test_cases = testCases
          .filter((tc) => tc.input.trim() || tc.expected_output.trim())
          .map(({ id: _drop, ...rest }) => rest);
        await adminCreateProblem(payload);
        toast?.("Problem created", "success");
      }
      navigate("/admin/problems");
    } catch (e) {
      toast?.(e?.response?.data?.detail || "Save failed", "error");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Loading />;

  const visibleCount = testCases.filter((t) => !t.is_hidden).length;
  const hiddenCount = testCases.length - visibleCount;

  return (
    <div className="page-wrap max-w-3xl">
      <div className="flex items-center gap-3 fade-up">
        <Link to="/admin/problems" className="btn btn-ghost btn-icon shrink-0" title="Back to problems">
          ←
        </Link>
        <div className="page-header flex-1">
          <h1 className="page-title">{isEdit ? "Edit Problem" : "New Problem"}</h1>
          <p className="page-sub">
            {isEdit ? "Update the details, test cases, or access controls." : "Set up a new coding practice problem."}
          </p>
        </div>
        {!isEdit && (
          <button
            type="button"
            onClick={() => setShowLeetCodeModal(true)}
            className="btn btn-ghost shrink-0"
          >
            📥 Import from LeetCode
          </button>
        )}
      </div>

      {showLeetCodeModal && (
        <LeetCodeImportModal onClose={() => setShowLeetCodeModal(false)} onImport={handleImport} />
      )}

      {/* Basic info */}
      <div className="glass-panel p-6 flex flex-col gap-4 fade-up-1">
        <h2 className="font-head font-semibold text-white/80">Basic Info</h2>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Title">
            <input className="input" value={form.title} onChange={(e) => updateField("title", e.target.value)} />
          </Field>
          <Field label="Slug">
            <input className="input" value={form.slug} onChange={(e) => updateField("slug", e.target.value)} />
          </Field>

          <Field label="Difficulty">
            <select
              className="input"
              value={form.difficulty}
              onChange={(e) => updateField("difficulty", e.target.value)}
            >
              <option value="basic" className="bg-space-900">Basic</option>
              <option value="intermediate" className="bg-space-900">Intermediate</option>
              <option value="advanced" className="bg-space-900">Advanced</option>
            </select>
          </Field>

          <Field label="Topic">
            <select
              className="input"
              value={form.topic_id}
              onChange={(e) => updateField("topic_id", e.target.value)}
            >
              <option value="">Select topic</option>
              {topics.map((t) => (
                <option key={t.id} value={t.id} className="bg-space-900">
                  {t.name}
                </option>
              ))}
            </select>
          </Field>
        </div>

        <div className="flex gap-2 items-end">
          <div className="input-group flex-1">
            <span className="input-label">New topic</span>
            <input
              className="input"
              placeholder="e.g. Loops"
              value={newTopicName}
              onChange={(e) => setNewTopicName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreateTopic()}
            />
          </div>
          <button type="button" onClick={handleCreateTopic} className="btn btn-ghost">
            + Add topic
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="glass-panel p-6 flex flex-col gap-4 fade-up-2">
        <h2 className="font-head font-semibold text-white/80">Content</h2>
        <Field label="Description (markdown)">
          <textarea
            rows={6}
            className="input font-mono text-xs"
            value={form.description}
            onChange={(e) => updateField("description", e.target.value)}
          />
        </Field>
        <Field label="Constraints (optional)">
          <textarea
            rows={2}
            className="input font-mono text-xs"
            value={form.constraints}
            onChange={(e) => updateField("constraints", e.target.value)}
          />
        </Field>
        <Field label="Starter code (optional)">
          <textarea
            rows={4}
            className="input font-mono text-xs"
            value={form.starter_code}
            onChange={(e) => updateField("starter_code", e.target.value)}
          />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Time limit (ms)">
            <input
              type="number"
              className="input"
              value={form.time_limit_ms}
              onChange={(e) => updateField("time_limit_ms", Number(e.target.value))}
            />
          </Field>
          <Field label="Memory limit (KB)">
            <input
              type="number"
              className="input"
              value={form.memory_limit_kb}
              onChange={(e) => updateField("memory_limit_kb", Number(e.target.value))}
            />
          </Field>
        </div>
      </div>

      {/* Access control */}
      <div className="glass-panel p-6 flex flex-col gap-3 fade-up-2">
        <h2 className="font-head font-semibold text-white/80">Access Control</h2>
        <Field label={isEdit ? "New access password" : "Access password (leave blank for an open problem)"}>
          <input
            type="text"
            className="input"
            placeholder={isEdit ? "Leave blank to keep current password" : "Optional"}
            value={form.access_password}
            onChange={(e) => updateField("access_password", e.target.value)}
            disabled={clearPassword}
          />
        </Field>
        {isEdit && (
          <label className="flex items-center gap-2 text-sm text-white/60">
            <input
              type="checkbox"
              checked={clearPassword}
              onChange={(e) => setClearPassword(e.target.checked)}
            />
            Remove password gate — make this problem open to everyone
          </label>
        )}
      </div>

      {/* Languages */}
      <div className="glass-panel p-6 flex flex-col gap-3 fade-up-2">
        <h2 className="font-head font-semibold text-white/80">Languages</h2>
        <p className="text-xs text-white/40">
          Leave everything unchecked to let users pick any supported language. Check exactly
          one to lock the problem to that language. Check several to offer a subset with an
          optional default.
        </p>
        <div className="flex gap-4 flex-wrap">
          {ALL_LANGUAGES.map((l) => (
            <label key={l.value} className="flex items-center gap-2 text-sm text-white/60">
              <input
                type="checkbox"
                checked={form.allowed_languages.includes(l.value)}
                onChange={() => toggleLanguage(l.value)}
              />
              {l.label}
            </label>
          ))}
        </div>
        {form.allowed_languages.length > 1 && (
          <Field label="Default language (preselected for users)">
            <select
              className="input"
              value={form.default_language}
              onChange={(e) => updateField("default_language", e.target.value)}
            >
              <option value="">No preference (first checked language)</option>
              {ALL_LANGUAGES.filter((l) => form.allowed_languages.includes(l.value)).map((l) => (
                <option key={l.value} value={l.value} className="bg-space-900">
                  {l.label}
                </option>
              ))}
            </select>
          </Field>
        )}
      </div>

      {/* Test cases */}
      <div className="glass-panel p-6 flex flex-col gap-4 fade-up-3">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h2 className="font-head font-semibold text-white/80">
            Test Cases{" "}
            <span className="text-xs font-normal text-white/40">
              ({visibleCount} visible, {hiddenCount} hidden)
            </span>
          </h2>
          <button type="button" onClick={addTestCase} className="btn btn-ghost btn-sm">
            + Add test case
          </button>
        </div>

        <div className="flex flex-col gap-3">
          {testCases.map((tc, i) => (
            <div key={i} className="glass rounded-2xl p-4">
              <div className="flex justify-between items-center mb-3">
                <label className="flex items-center gap-2 text-sm text-white/60">
                  <input
                    type="checkbox"
                    checked={tc.is_hidden}
                    onChange={(e) => updateTestCase(i, "is_hidden", e.target.checked)}
                  />
                  Hidden (used only on Submit)
                </label>
                <button
                  type="button"
                  onClick={() => removeTestCase(i)}
                  className="btn btn-danger btn-sm"
                >
                  Remove
                </button>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="input-group">
                  <span className="input-label">Input</span>
                  <textarea
                    rows={3}
                    className="input font-mono text-xs"
                    value={tc.input}
                    onChange={(e) => updateTestCase(i, "input", e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <span className="input-label">Expected output</span>
                  <textarea
                    rows={3}
                    className="input font-mono text-xs"
                    value={tc.expected_output}
                    onChange={(e) => updateTestCase(i, "expected_output", e.target.value)}
                  />
                </div>
              </div>
              <div className="mt-3 flex items-center gap-2 text-sm text-white/60">
                Points
                <input
                  type="number"
                  className="input w-20"
                  value={tc.points}
                  onChange={(e) => updateTestCase(i, "points", Number(e.target.value))}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end gap-3 pb-4">
        <Link to="/admin/problems" className="btn btn-ghost">
          Cancel
        </Link>
        <button onClick={handleSave} disabled={saving} className="btn btn-primary">
          {saving ? <Spinner sm /> : isEdit ? "Save Changes" : "Create Problem"}
        </button>
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="input-group block">
      <span className="input-label">{label}</span>
      {children}
    </label>
  );
}
