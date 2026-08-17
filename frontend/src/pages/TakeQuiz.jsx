import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useData } from '../context/DataContext'
import { Loading, DiffBadge, Spinner } from '../components/Shared'
import QuizPermissions from '../components/QuizPermissions'
import QuestionText from '../components/QuestionText'
import { shuffleQuizQuestions } from '../utils/shuffle'

const KEYS = ['A', 'B', 'C', 'D']
// Seconds to count down on the tab-switch overlay before auto-resuming
const TAB_COUNTDOWN_SECS = 10

// ─── timer ────────────────────────────────────────────────────────────────────
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
  return (
    <div className={`timer ${secs < 60 ? 'danger' : secs < 300 ? 'warning' : ''}`}>
      ⏱ {m}:{s}
    </div>
  )
}

// ─── quit confirmation dialog ─────────────────────────────────────────────────
function QuitDialog({ onStay, onQuit, submitting }) {
  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/60 backdrop-blur-md">
      <div className="glass-panel w-full max-w-sm mx-4 p-8 text-center shadow-glass-lg animate-[fadeUp_0.2s_ease-out]">
        <div className="text-4xl mb-4">⚠️</div>
        <h2 className="font-head font-bold text-xl text-white/90 mb-2">Quit the quiz?</h2>
        <p className="text-sm text-white/50 mb-8">
          You exited fullscreen. If you quit now your current answers will be submitted.
        </p>
        <div className="flex flex-col gap-3">
          <button
            className="btn btn-primary w-full"
            onClick={onStay}
          >
            🔒 Stay &amp; Re-enter Fullscreen
          </button>
          <button
            className="btn btn-ghost w-full text-rose-400 hover:text-rose-300"
            onClick={onQuit}
            disabled={submitting}
          >
            {submitting ? <Spinner sm /> : '✓ Submit &amp; Quit'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── tab-switch overlay ───────────────────────────────────────────────────────
function TabSwitchOverlay({ count, countdown }) {
  return (
    <div className="fixed inset-0 z-[200] flex flex-col items-center justify-center bg-black/70 backdrop-blur-xl">
      <div className="glass-panel w-full max-w-sm mx-4 p-8 text-center shadow-glass-lg animate-[fadeUp_0.2s_ease-out]">
        <div className="text-5xl mb-4">🚫</div>
        <h2 className="font-head font-bold text-xl text-white/90 mb-2">Tab switch detected!</h2>
        <p className="text-sm text-white/50 mb-1">
          Switching tabs is not allowed during the quiz.
        </p>
        <p className="text-sm text-rose-400 font-semibold mb-6">
          Violation #{count}
        </p>
        {/* countdown ring */}
        <div className="flex items-center justify-center mb-4">
          <div className="relative w-20 h-20">
            <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="6" />
              <circle
                cx="40" cy="40" r="34"
                fill="none"
                stroke="rgb(248 113 113)"
                strokeWidth="6"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 34}`}
                strokeDashoffset={`${2 * Math.PI * 34 * (1 - countdown / TAB_COUNTDOWN_SECS)}`}
                style={{ transition: 'stroke-dashoffset 1s linear' }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center font-head font-bold text-2xl text-white">
              {countdown}
            </div>
          </div>
        </div>
        <p className="text-xs text-white/35">Returning to quiz in {countdown}s…</p>
      </div>
    </div>
  )
}

// ─── main component ───────────────────────────────────────────────────────────
export default function TakeQuiz() {
  const { id }         = useParams()
  const { token }      = useAuth()
  const navigate       = useNavigate()
  const toast          = useToast()
  const { myResults }  = useData()

  const [quiz,        setQuiz]        = useState(null)
  const [attempt,     setAttempt]     = useState(null)
  const [answers,     setAnswers]     = useState({})
  const [current,     setCurrent]     = useState(0)
  const [loading,     setLoading]     = useState(true)
  const [submitting,  setSubmitting]  = useState(false)
  const [error,       setError]       = useState('')
  const [ready,       setReady]       = useState(false)

  // quit dialog — shown when user presses Esc / exits fullscreen
  const [showQuit,    setShowQuit]    = useState(false)

  // tab-switch overlay
  const [tabCount,    setTabCount]    = useState(0)
  const [tabOverlay,  setTabOverlay]  = useState(false)   // overlay visible?
  const [tabCountdown,setTabCountdown]= useState(TAB_COUNTDOWN_SECS)
  const tabCountRef   = useRef(0)
  const tabTimerRef   = useRef(null)

  // ── load quiz + attempt ─────────────────────────────────────────────────────
  // Sequential on purpose: userQuiz first (read-only), then startQuiz.
  // Promise.all fired both concurrently which caused two simultaneous POST
  // /start requests → race on the unique index → IntegrityError on first load.
  useEffect(() => {
    const init = async () => {
      try {
        const q = await api.userQuiz(token, id)
        const a = await api.startQuiz(token, id)
        setQuiz({ ...q, questions: shuffleQuizQuestions(q.questions) })
        setAttempt(a)
        if (a.answers)
          setAnswers(Object.fromEntries(
            Object.entries(a.answers).map(([k, v]) => [Number(k), v])
          ))
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [id])

  // ── submit ──────────────────────────────────────────────────────────────────
  const submit = useCallback(async () => {
    if (submitting) return
    setSubmitting(true)
    // always exit fullscreen before navigating away
    if (document.fullscreenElement) {
      await document.exitFullscreen().catch(() => {})
    }
    try {
      await api.submitQuiz(token, attempt.id, answers)
      myResults.refresh()
      toast('Quiz submitted! 🎉', 'success')
      navigate(`/results/${attempt.id}`)
    } catch (e) {
      toast(e.message, 'error')
      setSubmitting(false)
    }
  }, [attempt, answers, submitting])

  // ── fullscreen change — show quit dialog if user escapes ───────────────────
  useEffect(() => {
    if (!ready) return
    const onFsChange = () => {
      if (!document.fullscreenElement) {
        // User pressed Esc or used browser controls — ask what to do
        setShowQuit(true)
      }
    }
    document.addEventListener('fullscreenchange', onFsChange)
    return () => document.removeEventListener('fullscreenchange', onFsChange)
  }, [ready])

  // ── re-enter fullscreen when user chooses to stay ──────────────────────────
  const handleStay = async () => {
    setShowQuit(false)
    try {
      await document.documentElement.requestFullscreen()
    } catch {
      // If it fails for any reason just leave — don't lock the user out
    }
  }

  // ── quit = submit + leave ──────────────────────────────────────────────────
  const handleQuit = () => {
    setShowQuit(false)
    submit()
  }

  // ── tab-switch overlay logic ───────────────────────────────────────────────
  const dismissTabOverlay = useCallback(() => {
    clearInterval(tabTimerRef.current)
    setTabOverlay(false)
    setTabCountdown(TAB_COUNTDOWN_SECS)
  }, [])

  const handleTabSwitch = useCallback(() => {
    if (!ready) return
    // increment violation count
    tabCountRef.current += 1
    setTabCount(tabCountRef.current)

    // show the blur overlay
    setTabOverlay(true)
    setTabCountdown(TAB_COUNTDOWN_SECS)

    // start 10-second countdown, then auto-dismiss
    clearInterval(tabTimerRef.current)
    let remaining = TAB_COUNTDOWN_SECS
    tabTimerRef.current = setInterval(() => {
      remaining -= 1
      setTabCountdown(remaining)
      if (remaining <= 0) {
        dismissTabOverlay()
      }
    }, 1000)
  }, [ready, dismissTabOverlay])

  // cleanup tab timer on unmount
  useEffect(() => () => clearInterval(tabTimerRef.current), [])

  // ── hide sidebar + bottomnav while the quiz is active ──────────────────────
  useEffect(() => {
    if (!ready) return
    document.body.classList.add('quiz-active')
    return () => document.body.classList.remove('quiz-active')
  }, [ready])

  // ── exit fullscreen on unmount ─────────────────────────────────────────────
  useEffect(() => {
    return () => {
      clearInterval(tabTimerRef.current)
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {})
      }
    }
  }, [])

  // ── answer selection ────────────────────────────────────────────────────────
  const select = (q, displayIdx) => {
    const originalIdx = q.optionOrder ? q.optionOrder[displayIdx] : displayIdx
    setAnswers(a => ({ ...a, [q.id]: originalIdx }))
  }

  // ── states ──────────────────────────────────────────────────────────────────
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

  if (!ready) {
    return (
      <QuizPermissions
        onReady={() => setReady(true)}
        onTabSwitch={handleTabSwitch}
        requireCamera={false}
      />
    )
  }

  const q        = quiz.questions[current]
  const answered = Object.keys(answers).length
  const total    = quiz.questions.length

  return (
    <>
      {showQuit && (
        <QuitDialog
          onStay={handleStay}
          onQuit={handleQuit}
          submitting={submitting}
        />
      )}
      {tabOverlay && (
        <TabSwitchOverlay
          count={tabCount}
          countdown={tabCountdown}
        />
      )}

      <style>{`
        :fullscreen aside,
        :fullscreen nav.bottom-nav,
        :-webkit-full-screen aside,
        :-webkit-full-screen nav.bottom-nav,
        :-moz-full-screen aside,
        :-moz-full-screen nav.bottom-nav {
          display: none !important;
        }
        :fullscreen main,
        :-webkit-full-screen main,
        :-moz-full-screen main {
          padding-left: 1rem !important;
          padding-top: 1rem !important;
        }
      `}</style>

      <div className="page-wrap max-w-[860px]">
        <div className="flex flex-wrap justify-between items-start gap-3 fade-up mb-6">
          <div className="min-w-0">
            <div className="flex items-center gap-1 mb-1 flex-wrap">
              <DiffBadge level={quiz.difficulty} />
              <span className="tag">{quiz.subject}</span>
              {tabCount > 0 && (
                <span className="rounded-full bg-rose-500/20 border border-rose-500/30 px-2 py-0.5 text-[0.68rem] font-semibold text-rose-300">
                  ⚠ {tabCount} tab switch{tabCount > 1 ? 'es' : ''}
                </span>
              )}
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
                  <button
                    key={i}
                    className={`option-btn ${answers[q.id] === originalIdx ? 'selected' : ''}`}
                    onClick={() => select(q, i)}
                  >
                    <span className="option-key">{KEYS[i]}</span>
                    <span className="flex-1 text-left leading-normal">{opt}</span>
                  </button>
                )
              })}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                className="btn btn-ghost flex-1 sm:flex-initial"
                onClick={() => setCurrent(c => c - 1)}
                disabled={current === 0}
              >← Previous</button>
              {current < total - 1
                ? <button
                    className="btn btn-primary flex-1 sm:flex-initial"
                    onClick={() => setCurrent(c => c + 1)}
                  >Next →</button>
                : <button
                    className="btn btn-primary flex-1 sm:flex-initial"
                    onClick={submit}
                    disabled={submitting}
                  >
                    {submitting ? <Spinner sm /> : '✓ Submit Quiz'}
                  </button>
              }
            </div>
          </div>

          <div className="glass-panel fade-up-3 p-6 md:sticky md:top-6">
            <div className="text-xs text-white/40 font-semibold tracking-wide uppercase mb-3">Questions</div>
            <div className="q-nav mb-4">
              {quiz.questions.map((qq, i) => (
                <div
                  key={i}
                  className={`q-dot ${i === current ? 'current' : answers[qq.id] !== undefined ? 'answered' : ''}`}
                  onClick={() => setCurrent(i)}
                >{i + 1}</div>
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
    </>
  )
}
