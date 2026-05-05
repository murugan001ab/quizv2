import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { Loading, DiffBadge, Spinner } from '../components/Shared'

const KEYS = ['A', 'B', 'C', 'D']

function Timer({ end, onExpire }) {
  const calc = () => Math.max(0, Math.floor((new Date(end) - Date.now()) / 1000))
  const [secs, setSecs] = useState(calc)

  useEffect(() => {
    if (!end) return
    const t = setInterval(() => {
      const s = calc()
      setSecs(s)
      if (s <= 0) { clearInterval(t); onExpire() }
    }, 1000)
    return () => clearInterval(t)
  }, [end])

  if (!end) return null
  const m = String(Math.floor(secs / 60)).padStart(2, '0')
  const s = String(secs % 60).padStart(2, '0')
  const cls = secs < 60 ? 'danger' : secs < 300 ? 'warning' : ''
  return <div className={`timer ${cls}`}>⏱ {m}:{s}</div>
}

export default function TakeQuiz() {
  const { id } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()
  const toast = useToast()

  const [quiz, setQuiz] = useState(null)
  const [attempt, setAttempt] = useState(null)
  const [answers, setAnswers] = useState({})
  const [current, setCurrent] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const init = async () => {
      try {
        const q = await api.userQuiz(token, id)
        const a = await api.startQuiz(token, id)
        setQuiz(q)
        setAttempt(a)
        if (a.answers) setAnswers(Object.fromEntries(Object.entries(a.answers).map(([k, v]) => [Number(k), v])))
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [id])

  const select = (qId, opt) => {
    setAnswers(a => ({ ...a, [qId]: opt }))
  }

  const submit = useCallback(async () => {
    if (submitting) return
    setSubmitting(true)
    try {
      await api.submitQuiz(token, attempt.id, answers)
      toast('Quiz submitted! 🎉', 'success')
      navigate(`/results/${attempt.id}`)
    } catch (e) {
      toast(e.message, 'error')
      setSubmitting(false)
    }
  }, [attempt, answers, submitting])

  if (loading) return <Loading />
  if (error) return (
    <div className="page-wrap">
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🔒</div>
        <h2 style={{ fontFamily: 'var(--font-head)', marginBottom: '0.5rem' }}>Access Restricted</h2>
        <p style={{ color: 'var(--text3)', marginBottom: '1.5rem' }}>{error}</p>
        <button className="btn btn-ghost" onClick={() => navigate('/quizzes')}>← Back to Quizzes</button>
      </div>
    </div>
  )

  const q = quiz.questions[current]
  const answered = Object.keys(answers).length
  const total = quiz.questions.length

  return (
    <div className="page-wrap" style={{ maxWidth: 860 }}>
      {/* Header */}
      <div className="flex justify-between items-center fade-up" style={{ marginBottom: '1.5rem' }}>
        <div>
          <div className="flex items-center gap-1" style={{ marginBottom: '0.25rem' }}>
            <DiffBadge level={quiz.difficulty} />
            <span className="tag">{quiz.subject}</span>
          </div>
          <h1 style={{ fontFamily: 'var(--font-head)', fontWeight: 800, fontSize: '1.4rem' }}>{quiz.title}</h1>
        </div>
        <Timer end={quiz.scheduled_end} onExpire={submit} />
      </div>

      {/* Progress */}
      <div className="fade-up-1" style={{ marginBottom: '1.5rem' }}>
        <div className="flex justify-between items-center" style={{ marginBottom: '0.5rem', fontSize: '0.8rem', color: 'var(--text3)' }}>
          <span>Question {current + 1} of {total}</span>
          <span>{answered}/{total} answered</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${((current + 1) / total) * 100}%` }} />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 200px', gap: '1.5rem', alignItems: 'start' }}>
        {/* Question */}
        <div className="fade-up-2">
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text3)', marginBottom: '0.75rem', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              Q{current + 1}
            </div>
            <p style={{ fontSize: '1.05rem', lineHeight: 1.7, fontWeight: 500 }}>{q.text}</p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
            {q.options.map((opt, i) => (
              <button key={i}
                className={`option-btn ${answers[q.id] === i ? 'selected' : ''}`}
                onClick={() => select(q.id, i)}
              >
                <span className="option-key">{KEYS[i]}</span>
                {opt}
              </button>
            ))}
          </div>

          {/* Nav buttons */}
          <div className="flex justify-between" style={{ marginTop: '1.5rem' }}>
            <button className="btn btn-ghost" onClick={() => setCurrent(c => c - 1)} disabled={current === 0}>← Previous</button>
            {current < total - 1
              ? <button className="btn btn-primary" onClick={() => setCurrent(c => c + 1)}>Next →</button>
              : <button className="btn btn-primary" onClick={submit} disabled={submitting}>
                  {submitting ? <Spinner sm /> : '✓ Submit Quiz'}
                </button>
            }
          </div>
        </div>

        {/* Question navigator */}
        <div className="card fade-up-3" style={{ position: 'sticky', top: '1.5rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text3)', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
            Questions
          </div>
          <div className="q-nav" style={{ marginBottom: '1rem' }}>
            {quiz.questions.map((qq, i) => (
              <div key={i}
                className={`q-dot ${i === current ? 'current' : answers[qq.id] !== undefined ? 'answered' : ''}`}
                onClick={() => setCurrent(i)}
              >
                {i + 1}
              </div>
            ))}
          </div>
          <div className="divider" />
          <div style={{ fontSize: '0.75rem', color: 'var(--text3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              <div className="q-dot answered" style={{ width: 16, height: 16, fontSize: '0' }} /> Answered
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div className="q-dot" style={{ width: 16, height: 16, fontSize: '0' }} /> Unanswered
            </div>
          </div>
          <div className="divider" />
          <button className="btn btn-primary w-full" onClick={submit} disabled={submitting}>
            {submitting ? <Spinner sm /> : `Submit (${answered}/${total})`}
          </button>
        </div>
      </div>
    </div>
  )
}
