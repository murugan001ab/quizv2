import { useEffect, useState } from 'react'
import { api } from '../../api'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../context/ToastContext'
import { Loading, DiffBadge, Modal, Spinner } from '../../components/Shared'

const DIFFS = ['easy', 'medium', 'hard']
const SUBJECTS = ['Tamil', 'Science', 'Physics', 'Maths', 'Biology', 'Chemistry', 'History', 'English']
const KEYS = ['A', 'B', 'C', 'D']
const emptyQuiz = { title: '', description: '', subject: 'Maths', topic: '', difficulty: 'medium', scheduled_start: '', scheduled_end: '' }

// ── Attempts modal ───────────────────────────────────────────────────────────
function AttemptsModal({ quizId, quizTitle, token, onClose }) {
  const [attempts, setAttempts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.quizAttempts(token, quizId).then(setAttempts).catch(() => setAttempts([])).finally(() => setLoading(false))
  }, [quizId])

  return (
    <Modal title={`Attempts — ${quizTitle}`} onClose={onClose}>
      {loading ? <Loading /> : attempts.length === 0
        ? <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text3)' }}>No attempts yet.</div>
        : <div className="table-wrap">
          <table>
            <thead><tr><th>User</th><th>Score</th><th>%</th><th>Submitted</th></tr></thead>
            <tbody>
              {attempts.map(a => {
                const pct = a.total ? Math.round((a.score / a.total) * 100) : null
                const color = pct == null ? 'var(--text3)' : pct >= 80 ? 'var(--accent)' : pct >= 60 ? 'var(--blue)' : pct >= 40 ? 'var(--yellow)' : 'var(--red)'
                return (
                  <tr key={a.id}>
                    <td style={{ color: 'var(--text)', fontWeight: 500 }}>{a.username}</td>
                    <td>{a.submitted_at ? `${a.score}/${a.total}` : <span style={{ color: 'var(--accent)', fontSize: '0.75rem' }}>In progress</span>}</td>
                    <td>{pct != null && a.submitted_at ? <span style={{ fontFamily: 'var(--font-head)', fontWeight: 700, color }}>{pct}%</span> : '—'}</td>
                    <td>{a.submitted_at ? new Date(a.submitted_at).toLocaleString() : '—'}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      }
    </Modal>
  )
}

// ── Question editor modal ────────────────────────────────────────────────────
function QuestionModal({ quizId, editQ, token, toast, onClose, onSaved }) {
  const [form, setForm] = useState(editQ
    ? { text: editQ.text, options: [...editQ.options], correct_option: editQ.correct_option, explanation: editQ.explanation || '' }
    : { text: '', options: ['', '', '', ''], correct_option: 0, explanation: '' }
  )
  const [saving, setSaving] = useState(false)
  const setOpt = (i, val) => setForm(f => { const opts = [...f.options]; opts[i] = val; return { ...f, options: opts } })

  const save = async () => {
    if (!form.text.trim()) return toast('Question text is required', 'error')
    if (form.options.some(o => !o.trim())) return toast('All 4 options are required', 'error')
    setSaving(true)
    try {
      if (editQ) await api.updateQuestion(token, editQ.id, form)
      else await api.addQuestion(token, quizId, form)
      toast(editQ ? 'Question updated!' : 'Question added!', 'success')
      onSaved()
    } catch (e) { toast(e.message, 'error') }
    finally { setSaving(false) }
  }

  return (
    <Modal title={editQ ? 'Edit Question' : 'Add Question'} onClose={onClose}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="input-group">
          <label className="input-label">Question Text</label>
          <textarea className="input" rows={3} value={form.text} onChange={e => setForm(f => ({ ...f, text: e.target.value }))} placeholder="Enter the question..." style={{ resize: 'vertical' }} />
        </div>
        <div>
          <label className="input-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Options — click letter to mark correct answer</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {form.options.map((opt, i) => (
              <div key={i} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button onClick={() => setForm(f => ({ ...f, correct_option: i }))}
                  style={{
                    width: 32, height: 32, borderRadius: 6, flexShrink: 0, border: 'none', cursor: 'pointer',
                    background: form.correct_option === i ? 'var(--accent)' : 'var(--card2)',
                    color: form.correct_option === i ? '#0a0a0f' : 'var(--text3)',
                    fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: '0.75rem',
                    transition: 'all var(--transition)',
                  }}>{KEYS[i]}</button>
                <input className="input" value={opt} onChange={e => setOpt(i, e.target.value)} placeholder={`Option ${KEYS[i]}`} style={{ flex: 1 }} />
              </div>
            ))}
          </div>
        </div>
        <div className="input-group">
          <label className="input-label">Explanation (optional)</label>
          <input className="input" value={form.explanation} onChange={e => setForm(f => ({ ...f, explanation: e.target.value }))} placeholder="Why is the correct answer right?" />
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={save} disabled={saving}>
            {saving ? <Spinner sm /> : editQ ? 'Save Changes' : 'Add Question'}
          </button>
        </div>
      </div>
    </Modal>
  )
}

// ── Quiz detail / question manager ───────────────────────────────────────────
function QuizDetail({ quiz, token, toast, onBack, onUpdated }) {
  const [questions, setQuestions] = useState(quiz.questions || [])
  const [showAddQ, setShowAddQ] = useState(false)
  const [editQ, setEditQ] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const reload = async () => {
    try {
      const q = await api.adminQuiz(token, quiz.id)
      setQuestions(q.questions || [])
      console.log(q)
    }
    catch (e) {
      toast(e.message, 'error')
    }
  }

  const deleteQ = async (qId) => {
    setDeleting(qId)
    try { await api.deleteQuestion(token, qId); toast('Question deleted', 'success'); setQuestions(qs => qs.filter(q => q.id !== qId)) }
    catch (e) { toast(e.message, 'error') }
    finally { setDeleting(null) }
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
        <button className="btn btn-ghost btn-sm" onClick={onBack}>← Back</button>
        <div>
          <h2 style={{ fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: '1.25rem' }}>{quiz.title}</h2>
          <div style={{ fontSize: '0.8rem', color: 'var(--text3)', marginTop: '0.2rem' }}>{questions.length} question{questions.length !== 1 ? 's' : ''}</div>
        </div>
        <button className="btn btn-primary btn-sm" style={{ marginLeft: 'auto' }} onClick={() => setShowAddQ(true)}>+ Add Question</button>
      </div>

      {questions.length === 0
        ? <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text3)' }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>📝</div>
          No questions yet — add the first one!
        </div>
        : <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
          {questions.map((q, i) => (
            <div key={q.id} className="card fade-up" style={{ animationDelay: `${i * 0.03}s` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text3)', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.375rem' }}>Q{i + 1}</div>
                  <p style={{ fontWeight: 500, marginBottom: '0.75rem', lineHeight: 1.6 }}>{q.text}</p>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.375rem' }}>
                    {q.options.map((opt, j) => (
                      <div key={j} style={{
                        display: 'flex', alignItems: 'center', gap: '0.5rem',
                        padding: '0.375rem 0.625rem',
                        background: q.correct_option === j ? 'rgba(52,211,153,0.1)' : 'var(--bg3)',
                        border: `1px solid ${q.correct_option === j ? 'rgba(52,211,153,0.3)' : 'var(--border)'}`,
                        borderRadius: 6, fontSize: '0.8rem',
                      }}>
                        <span style={{
                          width: 20, height: 20, borderRadius: 4, flexShrink: 0,
                          background: q.correct_option === j ? 'var(--accent2)' : 'var(--card2)',
                          color: q.correct_option === j ? '#0a0a0f' : 'var(--text3)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: '0.65rem', fontWeight: 700, fontFamily: 'var(--font-head)',
                        }}>{KEYS[j]}</span>
                        <span style={{ color: q.correct_option === j ? 'var(--accent2)' : 'var(--text2)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{opt}</span>
                      </div>
                    ))}
                  </div>
                  {q.explanation && (
                    <div style={{ marginTop: '0.625rem', padding: '0.5rem 0.75rem', background: 'var(--bg3)', borderRadius: 6, fontSize: '0.8rem', color: 'var(--text3)', borderLeft: '2px solid var(--accent)' }}>
                      💡 {q.explanation}
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '0.375rem', flexShrink: 0 }}>
                  <button className="btn btn-ghost btn-sm" onClick={() => setEditQ(q)}>Edit</button>
                  <button className="btn btn-danger btn-sm" onClick={() => deleteQ(q.id)} disabled={deleting === q.id}>
                    {deleting === q.id ? <Spinner sm /> : 'Del'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      }

      {(showAddQ || editQ) && (
        <QuestionModal
          quizId={quiz.id} editQ={editQ} token={token} toast={toast}
          onClose={() => { setShowAddQ(false); setEditQ(null) }}
          onSaved={() => { setShowAddQ(false); setEditQ(null); reload(); onUpdated() }}
        />
      )}
    </div>
  )
}

// ── Quiz form modal ──────────────────────────────────────────────────────────
function QuizFormModal({ editQuiz, token, toast, onClose, onSaved }) {
  const [form, setForm] = useState(editQuiz ? {
    title: editQuiz.title, description: editQuiz.description || '',
    subject: editQuiz.subject, topic: editQuiz.topic || '', difficulty: editQuiz.difficulty,
    scheduled_start: editQuiz.scheduled_start ? editQuiz.scheduled_start.slice(0, 16) : '',
    scheduled_end: editQuiz.scheduled_end ? editQuiz.scheduled_end.slice(0, 16) : '',
  } : { ...emptyQuiz })
  const [saving, setSaving] = useState(false)
  const f = k => e => setForm(prev => ({ ...prev, [k]: e.target.value }))

  const save = async () => {
    if (!form.title.trim()) return toast('Title is required', 'error')
    setSaving(true)
    try {
      const payload = { ...form, scheduled_start: form.scheduled_start || null, scheduled_end: form.scheduled_end || null }
      if (editQuiz) await api.updateQuiz(token, editQuiz.id, payload)
      else await api.createQuiz(token, payload)
      toast(editQuiz ? 'Quiz updated!' : 'Quiz created!', 'success')
      onSaved()
    } catch (e) { toast(e.message, 'error') }
    finally { setSaving(false) }
  }

  return (
    <Modal title={editQuiz ? 'Edit Quiz' : 'Create New Quiz'} onClose={onClose}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="input-group">
          <label className="input-label">Title</label>
          <input className="input" value={form.title} onChange={f('title')} placeholder="e.g. Physics – Newton's Laws" />
        </div>
        <div className="input-group">
          <label className="input-label">Description</label>
          <textarea className="input" rows={2} value={form.description} onChange={f('description')} placeholder="Brief description..." style={{ resize: 'vertical' }} />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
          <div className="input-group">
            <label className="input-label">Subject</label>
            <select className="input" value={form.subject} onChange={f('subject')}>
              {SUBJECTS.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div className="input-group">
            <label className="input-label">Topic</label>
            <input className="input" value={form.topic} onChange={f('topic')} placeholder="e.g. Algebra" />
          </div>
          <div className="input-group">
            <label className="input-label">Difficulty</label>
            <select className="input" value={form.difficulty} onChange={f('difficulty')}>
              {DIFFS.map(d => <option key={d}>{d}</option>)}
            </select>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <div className="input-group">
            <label className="input-label">Scheduled Start</label>
            <input className="input" type="datetime-local" value={form.scheduled_start} onChange={f('scheduled_start')} />
          </div>
          <div className="input-group">
            <label className="input-label">Scheduled End</label>
            <input className="input" type="datetime-local" value={form.scheduled_end} onChange={f('scheduled_end')} />
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={save} disabled={saving}>
            {saving ? <Spinner sm /> : editQuiz ? 'Save Changes' : 'Create Quiz'}
          </button>
        </div>
      </div>
    </Modal>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function AdminQuizzes() {
  const { token } = useAuth()
  const toast = useToast()
  const [quizzes, setQuizzes] = useState([])
  const [loading, setLoading] = useState(true)
  const [filterDiff, setFilterDiff] = useState('All')
  const [filterSubject, setFilterSubject] = useState('All')
  const [showCreate, setShowCreate] = useState(false)
  const [editQuiz, setEditQuiz] = useState(null)
  const [attemptsModal, setAttemptsModal] = useState(null)
  const [detailQuiz, setDetailQuiz] = useState(null)
  const [deleting, setDeleting] = useState(null)

  const load = async () => {
    setLoading(true)

    const params = new URLSearchParams()

    if (filterDiff !== 'All') {
      params.set('difficulty', filterDiff)
    }

    if (filterSubject !== 'All') {
      params.set('subject', filterSubject)
    }

    const q = params.toString() ? `?${params}` : ''

    try {
      const data = await api.adminQuizzes(token, q)
      setQuizzes(data)
    }
    catch (e) {
      toast(e.message, 'error')
    }
    finally {
      setLoading(false)
    }
  }
  useEffect(() => { load() }, [filterDiff, filterSubject])

 const getQuetions = async (id) => {
  try {
    const q = await api.adminQuiz(token, id)
    setDetailQuiz(q)
  }
  catch (e) {
    toast(e.message, 'error')
  }
}

  const deleteQuiz = async (id) => {
    if (!window.confirm('Delete this quiz and all its questions?')) return
    setDeleting(id)
    try { await api.deleteQuiz(token, id); toast('Quiz deleted', 'success'); setQuizzes(qs => qs.filter(q => q.id !== id)) }
    catch (e) { toast(e.message, 'error') }
    finally { setDeleting(null) }
  }

  if (detailQuiz) return (
    <div className="page-wrap">
      <QuizDetail quiz={detailQuiz} token={token} toast={toast}
        onBack={() => { setDetailQuiz(null); load() }} onUpdated={load} />
    </div>
  )

  return (
    <div className="page-wrap">
      <div className="flex justify-between items-center fade-up" style={{ marginBottom: '2rem' }}>
        <div>
          <h1 className="page-title">Manage Quizzes</h1>
          <p className="page-sub">Create, edit, and manage quiz content</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ New Quiz</button>
      </div>

      <div className="flex gap-2 fade-up-1" style={{ marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <div className="input-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.5rem' }}>
          <label className="input-label" style={{ whiteSpace: 'nowrap' }}>Subject</label>
          <select className="input" value={filterSubject} onChange={e => setFilterSubject(e.target.value)} style={{ width: 'auto' }}>
            {['All', ...SUBJECTS].map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div className="input-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.5rem' }}>
          <label className="input-label" style={{ whiteSpace: 'nowrap' }}>Difficulty</label>
          <select className="input" value={filterDiff} onChange={e => setFilterDiff(e.target.value)} style={{ width: 'auto' }}>
            {['All', ...DIFFS].map(d => <option key={d}>{d}</option>)}
          </select>
        </div>
      </div>

      {loading ? <Loading /> : quizzes.length === 0
        ? <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text3)' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
          <div style={{ fontSize: '1.1rem', color: 'var(--text2)', marginBottom: '0.5rem' }}>No quizzes found</div>
          <div style={{ fontSize: '0.875rem', marginBottom: '1.5rem' }}>Create your first quiz to get started.</div>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Create Quiz</button>
        </div>
        : <div className="card fade-up-2" style={{ padding: 0 }}>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Title</th><th>Subject / Topic</th><th>Difficulty</th>
                  <th>Questions</th><th>Status</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {quizzes.map((q, i) => {
                  const now = new Date()
                  const start = q.scheduled_start ? new Date(q.scheduled_start) : null
                  const end = q.scheduled_end ? new Date(q.scheduled_end) : null
                  const isLive = (!start || now >= start) && (!end || now <= end)
                  const isUpcoming = start && now < start
                  const isEnded = end && now > end
                  return (
                    <tr key={q.id} className="fade-up" style={{ animationDelay: `${i * 0.03}s` }}>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          {q.title}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: '0.875rem' }}>{q.subject}</div>
                        {q.topic && <div style={{ fontSize: '0.75rem', color: 'var(--text3)' }}>{q.topic}</div>}
                      </td>
                      <td><DiffBadge level={q.difficulty} /></td>
                      <td>
                        <span style={{ fontFamily: 'var(--font-head)', fontWeight: 700 }}>{q.question_count ?? 0}</span>
                        <span style={{ color: 'var(--text3)', fontSize: '0.8rem' }}> Qs</span>
                      </td>
                      <td>
                        {isUpcoming && <span className="badge badge-blue">Upcoming</span>}
                        {isLive && !isEnded && (
                          <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.72rem', color: 'var(--accent)' }}>
                            <span className="live-dot" />LIVE
                          </span>
                        )}
                        {isEnded && <span className="badge badge-gray">Ended</span>}
                        {!start && !end && <span style={{ color: 'var(--text3)', fontSize: '0.8rem' }}>Always open</span>}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap' }}>
                          <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => {
                              getQuetions(q.id)
                              // console.log(q.id)
                            }}
                          >
                            Questions
                          </button>
                          <button className="btn btn-ghost btn-sm" onClick={() => setAttemptsModal(q)}>Attempts</button>
                          <button className="btn btn-ghost btn-sm" onClick={() => setEditQuiz(q)}>Edit</button>
                          <button className="btn btn-danger btn-sm" onClick={() => deleteQuiz(q.id)} disabled={deleting === q.id}>
                            {deleting === q.id ? <Spinner sm /> : 'Del'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      }

      {(showCreate || editQuiz) && (
        <QuizFormModal editQuiz={editQuiz} token={token} toast={toast}
          onClose={() => { setShowCreate(false); setEditQuiz(null) }}
          onSaved={() => { setShowCreate(false); setEditQuiz(null); load() }}
        />
      )}

      {attemptsModal && (
        <AttemptsModal quizId={attemptsModal.id} quizTitle={attemptsModal.title}
          token={token} onClose={() => setAttemptsModal(null)} />
      )}
    </div>
  )
}
