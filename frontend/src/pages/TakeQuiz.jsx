import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useData } from '../context/DataContext'
import { Loading, DiffBadge, Spinner } from '../components/Shared'
import QuestionText from '../components/QuestionText'
import { shuffleQuizQuestions } from '../utils/shuffle'

const KEYS = ['A', 'B', 'C', 'D']

function Timer({ end, onExpire }) {
  const calc = () => Math.max(0, Math.floor((new Date(end) - Date.now()) / 1000))
  const [secs, setSecs] = useState(calc)
  useEffect(() => {
    if (!end) return
    const t = setInterval(() => { const s = calc(); setSecs(s); if (s <= 0) { clearInterval(t); onExpire() } }, 1000)
    return () => clearInterval(t)
  }, [end])
  if (!end) return null
  const m = String(Math.floor(secs / 60)).padStart(2, '0')
  const s = String(secs % 60).padStart(2, '0')
  return <div className={`timer ${secs < 60 ? 'danger' : secs < 300 ? 'warning' : ''}`}>⏱ {m}:{s}</div>
}

export default function TakeQuiz() {
  const { id }    = useParams()
  const { token } = useAuth()
  const navigate  = useNavigate()
  const toast     = useToast()
  const { myResults } = useData()   // ← to invalidate cache after submit

  const [quiz,       setQuiz]       = useState(null)
  const [attempt,    setAttempt]    = useState(null)
  const [answers,    setAnswers]    = useState({})
  const [current,    setCurrent]    = useState(0)
  const [loading,    setLoading]    = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error,      setError]      = useState('')

  useEffect(() => {
    const init = async () => {
      try {
        const [q, a] = await Promise.all([
          api.userQuiz(token, id),
          api.startQuiz(token, id),
        ])
        // Shuffle question order + option order per attempt so users can't
        // just copy answer positions from each other. Shuffled once here and
        // kept in state, so it stays stable for the rest of the attempt.
        setQuiz({ ...q, questions: shuffleQuizQuestions(q.questions) })
        setAttempt(a)
        if (a.answers)
          setAnswers(Object.fromEntries(Object.entries(a.answers).map(([k, v]) => [Number(k), v])))
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [id])

  // `displayIdx` is the position shown on screen (post-shuffle). We store the
  // ORIGINAL option index in `answers` since that's what the backend expects
  // and what a resumed attempt's `a.answers` is already keyed by.
  const select = (q, displayIdx) => {
    const originalIdx = q.optionOrder ? q.optionOrder[displayIdx] : displayIdx
    setAnswers(a => ({ ...a, [q.id]: originalIdx }))
  }

  const submit = useCallback(async () => {
    if (submitting) return
    setSubmitting(true)
    try {
      await api.submitQuiz(token, attempt.id, answers)
      // Invalidate results cache so Results page shows new entry immediately
      myResults.refresh()
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
      <div className="glass-panel text-center p-12">
        <div className="text-3xl mb-4">🔒</div>
        <h2 className="font-head font-bold mb-2">Access Restricted</h2>
        <p className="text-white/40 mb-6">{error}</p>
        <button className="btn btn-ghost" onClick={() => navigate('/quizzes')}>← Back to Quizzes</button>
      </div>
    </div>
  )

  const q        = quiz.questions[current]
  const answered = Object.keys(answers).length
  const total    = quiz.questions.length

  return (
    <div className="page-wrap max-w-[860px]">
      <div className="flex flex-wrap justify-between items-start gap-3 fade-up mb-6">
        <div className="min-w-0">
          <div className="flex items-center gap-1 mb-1">
            <DiffBadge level={quiz.difficulty} />
            <span className="tag">{quiz.subject}</span>
          </div>
          <h1 className="font-head font-extrabold text-[1.15rem] sm:text-[1.4rem] break-words">{quiz.title}</h1>
        </div>
        <Timer end={quiz.scheduled_end} onExpire={submit} />
      </div>

      <div className="fade-up-1 mb-6">
        <div className="flex justify-between items-center mb-2 text-[0.8rem] text-white/40">
          <span>Question {current + 1} of {total}</span>
          <span>{answered}/{total} answered</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${((current + 1) / total) * 100}%` }} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-[1fr_200px] gap-6 items-start">
        <div className="fade-up-2">
          <div className="glass-panel p-6 mb-4">
            <div className="text-xs text-white/40 mb-3.5 font-semibold tracking-wide uppercase">
              Q{current + 1}
              {q.year && <span className="ml-2 text-accent-400 opacity-80">· {q.year}</span>}
            </div>
            <QuestionText text={q.text} />
          </div>
          <div className="flex flex-col gap-2.5">
            {q.options.map((opt, i) => {
              const originalIdx = q.optionOrder ? q.optionOrder[i] : i
              return (
                <button key={i} className={`option-btn ${answers[q.id] === originalIdx ? 'selected' : ''}`} onClick={() => select(q, i)}>
                  <span className="option-key">{KEYS[i]}</span>
                  <span className="flex-1 text-left leading-normal">{opt}</span>
                </button>
              )
            })}
          </div>
          <div className="flex gap-3 mt-6">
            <button className="btn btn-ghost flex-1 sm:flex-initial" onClick={() => setCurrent(c => c - 1)} disabled={current === 0}>← Previous</button>
            {current < total - 1
              ? <button className="btn btn-primary flex-1 sm:flex-initial" onClick={() => setCurrent(c => c + 1)}>Next →</button>
              : <button className="btn btn-primary flex-1 sm:flex-initial" onClick={submit} disabled={submitting}>
                  {submitting ? <Spinner sm /> : '✓ Submit Quiz'}
                </button>
            }
          </div>
        </div>

        <div className="glass-panel fade-up-3 p-6 md:sticky md:top-6">
          <div className="text-xs text-white/40 font-semibold tracking-wide uppercase mb-3">Questions</div>
          <div className="q-nav mb-4">
            {quiz.questions.map((qq, i) => (
              <div key={i} className={`q-dot ${i === current ? 'current' : answers[qq.id] !== undefined ? 'answered' : ''}`} onClick={() => setCurrent(i)}>{i + 1}</div>
            ))}
          </div>
          <div className="divider" />
          <div className="text-xs text-white/40">
            <div className="flex items-center gap-2 mb-1">
              <div className="q-dot answered w-4 h-4 text-[0]" /> Answered
            </div>
            <div className="flex items-center gap-2">
              <div className="q-dot w-4 h-4 text-[0]" /> Unanswered
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
