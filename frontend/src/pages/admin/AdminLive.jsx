import { useEffect, useState } from 'react'
import { api } from '../../api'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../context/ToastContext'
import { useLiveSocket } from '../../hooks/useLiveSocket'
import { Loading, Spinner } from '../../components/Shared'
import { useData } from '../../context/DataContext'
// Falls back to the current origin when VITE_URL isn't set (it's missing
// from .env.production), and is normalized to always end in exactly one
// slash so the concatenation below can't produce "...comlive/CODE" or
// "...com//live/CODE".
const FRONTEND_BASE = (import.meta.env.VITE_URL || (typeof window !== 'undefined' ? window.location.origin : '')).replace(/\/*$/, '/')
// ── Step 0: if this admin already has an open channel (e.g. they got
// disconnected, refreshed, or navigated away mid-session), let them
// reclaim it as host instead of being forced into creating a new one.
function MyChannelsPanel({ token,link, userId, toast, onRejoined,onCopy, refreshTick }) {
  const [channels, setChannels] = useState([])
  const [loading, setLoading] = useState(true)
  const [pending, setPending] = useState(null) // code currently being rejoined
  const [passwords, setPasswords] = useState({}) // code -> password draft

  useEffect(() => {
    let cancelled = false
    api.listLiveChannels(token)
      .then(list => {
        if (cancelled) return
        setChannels(list.filter(c => c.admin_user_id === userId && c.state !== 'finished'))
      })
      .catch(() => { /* silent — this panel is a convenience, not critical path */ })
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [token, userId, refreshTick])

  const rejoin = (ch) => {
    setPending(ch.code)
    onRejoined(ch, passwords[ch.code] || '')
  }

  if (loading || channels.length === 0) return null

  return (
    <div className="card fade-up" style={{ maxWidth: 480, marginBottom: '1.25rem' }}>
      <div style={{ fontSize: '0.72rem', color: 'var(--text3)', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
        Rejoin a channel you're already hosting 
      </div>
      <button onClick={()=>{onCopy(link)}}>copy</button>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
        {channels.map(ch => (
          <div key={ch.code} style={{
            display: 'flex', flexDirection: 'column', gap: '0.5rem',
            padding: '0.625rem 0.75rem', background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 6,
          }}>
            <div className="flex justify-between items-center">
              <div>
                <div style={{ fontWeight: 600 }}>{ch.name} <span style={{ color: 'var(--text3)', fontWeight: 400 }}>· {ch.code}</span></div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text3)' }}>{ch.quiz_title} · {ch.participant_count} connected · {ch.state}</div>
              </div>
              <button className="btn btn-primary btn-sm" disabled={pending === ch.code} onClick={() => rejoin(ch)}>
                {pending === ch.code ? <Spinner sm /> : 'Rejoin as host'}
              </button>
            </div>
            {ch.locked && (
              <input
                className="input"
                type="password"
                placeholder="Channel password"
                value={passwords[ch.code] || ''}
                onChange={e => setPasswords(p => ({ ...p, [ch.code]: e.target.value }))}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Step 1: pick a quiz, name the channel, optionally lock it ──────────────
function CreateChannelForm({ token, toast, onCreated }) {
  const [quizzes, setQuizzes] = useState([])
  const [loading, setLoading] = useState(true)
  
  const [quizId, setQuizId] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [timePerQuestion, setTimePerQuestion] = useState(20)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    api.adminQuizzes(token, '?quiz_type=live')
      .then(qs => {
        setQuizzes(qs)
        if (qs.length) setQuizId(String(qs[0].id))
      })
      .catch(e => toast(e.message, 'error'))
      .finally(() => setLoading(false))
  }, [])

  const create = async () => {
    if (!name.trim()) return toast('Channel name is required', 'error')
    if (!quizId) return toast('Pick a quiz', 'error')
    setCreating(true)
    try {
      const channel = await api.createLiveChannel(token, {
        name,
        quiz_id: Number(quizId),
        password: password || null,
        time_per_question: Number(timePerQuestion) || 20,
      })
      onCreated(channel, password)
    } catch (e) {
      toast(e.message, 'error')
    } finally {
      setCreating(false)
    }
  }

  if (loading) return <Loading />

  if (quizzes.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text3)' }}>
        <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>📡</div>
        You need at least one quiz marked as "Live" type (with questions) before starting a live channel.
        Set a quiz's type to Live from the Manage Quizzes page.
      </div>
    )
  }

  return (
    <div className="card fade-up" style={{ maxWidth: 480 }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="input-group">
          <label className="input-label">Quiz</label>
          <select className="input" value={quizId} onChange={e => setQuizId(e.target.value)}>
            {quizzes.map(q => (
              <option key={q.id} value={q.id}>
                {q.title} ({q.question_count ?? 0} questions)
              </option>
            ))}
          </select>
        </div>
        <div className="input-group">
          <label className="input-label">Channel name</label>
          <input className="input" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Period 3 – Live Round" />
        </div>
        <div className="input-group">
          <label className="input-label">Password (optional)</label>
          <input className="input" value={password} onChange={e => setPassword(e.target.value)} placeholder="Leave blank for an open channel" />
        </div>
        <div className="input-group">
          <label className="input-label">Seconds per question</label>
          <input className="input" type="number" min={5} value={timePerQuestion} onChange={e => setTimePerQuestion(e.target.value)} />
        </div>
        <button className="btn btn-primary w-full" onClick={create} disabled={creating}>
          {creating ? <Spinner sm /> : 'Create channel & open room'}
        </button>
      </div>
    </div>
  )
}

// ── Step 2: the live room (host view) ───────────────────────────────────────
function ExplainPanel({ q, onPrev, onNext }) {
  const total = q.counts.reduce((a, b) => a + b, 0)
  return (
    <div className="card fade-up">
      <div className="flex justify-between items-center" style={{ marginBottom: '0.75rem' }}>
        <div style={{ fontSize: '0.72rem', color: 'var(--text3)', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          Review · Question {q.index + 1} of {q.total}
        </div>
      </div>
      <p style={{ fontWeight: 600, marginBottom: '0.875rem' }}>{q.text}</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {q.options.map((opt, i) => {
          const count = q.counts[i] || 0
          const pct = total ? Math.round((count / total) * 100) : 0
          const isCorrect = i === q.correct_option
          return (
            <div key={i} style={{
              position: 'relative', overflow: 'hidden', padding: '0.5rem 0.75rem', borderRadius: 6,
              background: isCorrect ? 'rgba(52,211,153,0.1)' : 'var(--bg3)',
              border: `1px solid ${isCorrect ? 'rgba(52,211,153,0.4)' : 'var(--border)'}`,
              display: 'flex', justifyContent: 'space-between', gap: '0.5rem',
            }}>
              <span>{opt}</span>
              <span style={{ fontFamily: 'var(--font-head)', fontWeight: 700 }}>{count} · {pct}%</span>
            </div>
          )
        })}
      </div>
      {q.explanation && (
        <div style={{ marginTop: '0.875rem', padding: '0.75rem', background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 6, fontSize: '0.85rem', color: 'var(--text2)' }}>
          {q.explanation}
        </div>
      )}
      <div className="flex justify-between" style={{ marginTop: '1.25rem' }}>
        <button className="btn btn-ghost" onClick={onPrev} disabled={q.index === 0}>← Previous</button>
        <button className="btn btn-primary" onClick={onNext} disabled={q.index >= q.total - 1}>Next →</button>
      </div>
    </div>
  )
}

function HostRoom({ socket,link, channel, token,onCopy, toast, onReset }) {
  const {
    users, quizState, question, correctIndex, leaderboard, startQuiz, leave,
    explainQuestion, startExplain, explainNext, explainPrev,
  } = socket
  const [closing, setClosing] = useState(false)


  const doReset = async () => {
    setClosing(true)
    try {
      await api.closeLiveChannel(token, channel.code)
    } catch (e) {
      toast(e.message, 'error')
    } finally {
      leave()
      onReset()
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: 640 }}>
      <div className="card fade-up">
        <div className="flex justify-between items-center" style={{ marginBottom: '0.5rem' }}>
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text3)', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
              Join code
            </div>
            <div style={{ fontFamily: 'var(--font-head)', fontWeight: 800, fontSize: '2rem', letterSpacing: '0.1em' }}>
              {channel.code} <button onClick={()=>{onCopy(channel.code)}}>copy</button>
            </div>
            <button onClick={()=>{onCopy(link)}}>copy</button>
          </div>
          <span className={`badge ${channel.locked ? 'badge-gray' : 'badge-blue'}`}>
            {channel.locked ? '🔒 Password protected' : '🔓 Open'}
          </span>
        </div>
        <div style={{ color: 'var(--text3)', fontSize: '0.875rem' }}>{channel.quiz_title}</div>
      </div>

      <div className="card fade-up-1">
        <div className="flex justify-between items-center" style={{ marginBottom: '0.75rem' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text3)', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            Connected ({users.length})
          </div>
          {quizState === 'in_progress' && (
            <span className="flex items-center gap-1" style={{ fontSize: '0.72rem', color: 'var(--accent)' }}>
              <span className="live-dot" /> LIVE — Q{question ? question.index + 1 : '?'}/{question?.total ?? '?'}
            </span>
          )}
          {quizState === 'finished' && <span className="badge badge-gray">Finished</span>}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
          {users.map(u => (
            <div key={u.user_id} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '0.5rem 0.75rem', background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 6,
            }}>
              <span style={{ fontWeight: 500 }}>
                {u.username} {u.is_admin && <span style={{ color: 'var(--accent)', fontSize: '0.72rem' }}> (host)</span>}
              </span>
              {!u.is_admin && (
                <span style={{ fontFamily: 'var(--font-head)', fontWeight: 700, color: 'var(--text3)' }}>{u.score}</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {quizState === 'waiting' && (
        <button className="btn btn-primary w-full" onClick={startQuiz} disabled={users.length < 2}>
          {users.length < 2 ? 'Waiting for at least one participant…' : 'Start quiz'}
        </button>
      )}

      {question && quizState === 'in_progress' && (
        <div className="card fade-up-2">
          <div style={{ fontSize: '0.72rem', color: 'var(--text3)', marginBottom: '0.5rem' }}>Current question</div>
          <p style={{ fontWeight: 500, marginBottom: '0.75rem' }}>{question.text}</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.375rem' }}>
            {question.options.map((opt, i) => (
              <div key={i} style={{
                padding: '0.375rem 0.625rem', borderRadius: 6, fontSize: '0.8rem',
                background: correctIndex === i ? 'rgba(52,211,153,0.1)' : 'var(--bg3)',
                border: `1px solid ${correctIndex === i ? 'rgba(52,211,153,0.3)' : 'var(--border)'}`,
                color: correctIndex === i ? 'var(--accent2)' : 'var(--text2)',
              }}>{opt}</div>
            ))}
          </div>
        </div>
      )}

      {leaderboard.length > 0 && (
        <div className="card fade-up-3">
          <div style={{ fontSize: '0.72rem', color: 'var(--text3)', marginBottom: '0.5rem' }}>Leaderboard</div>
          <ol style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem', paddingLeft: '1.1rem' }}>
            {leaderboard.map((s, i) => (
              <li key={s.username} style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>{s.username}</span>
                <span style={{ fontWeight: 700 }}>{s.score}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {quizState === 'finished' && (
        explainQuestion ? (
          <ExplainPanel q={explainQuestion} onPrev={explainPrev} onNext={explainNext} />
        ) : (
          <button className="btn btn-primary w-full" onClick={startExplain}>
            📖 Start explanation walkthrough
          </button>
        )
      )}

      <button className="btn btn-ghost" onClick={doReset} disabled={closing}>
        {closing ? <Spinner sm /> : '← Close this channel & start a new one'}
      </button>
    </div>
  )
}

// ── Page ─────────────────────────────────────────────────────────────────────
export default function AdminLive() {
  const { token, user } = useAuth()
  const {link,setLink} =useData()
  const toast = useToast()
  const socket = useLiveSocket()
  const [channel, setChannel] = useState(null)
  // Bumped whenever a channel is created/closed so MyChannelsPanel refetches.
  const [refreshTick, setRefreshTick] = useState(0)
  const [isCopied, setIsCopied] = useState(false);

  const handleCreated = (created, password) => {
    setChannel(created)
    const link=FRONTEND_BASE+"live/"+created.code+"/"+created.link_token // FRONTEND_BASE always ends in "/" now
    console.log("link is",link)
    setLink(link)
    socket.join(created.code, token, password)
    setRefreshTick(t => t + 1)
  }

  // Reclaiming an existing channel — same join flow as creating one, just
  // sourced from the channel summary instead of the create-channel response.
  const handleRejoined = (summary, password) => {
    setChannel(summary)
   
    socket.join(summary.code, token, password)
  }

  const handleReset = () => {
    setChannel(null)
    setRefreshTick(t => t + 1)

  }

  const handleCopy = async (textToCopy) => {
    try {
      await navigator.clipboard.writeText(textToCopy);
      setIsCopied(true);
      toast('copyed')
      setTimeout(() => setIsCopied(false), 2000); // Reset status after 2 seconds
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  useEffect(() => {
    if (socket.error) toast(socket.error, 'error')
  }, [socket.error])

  return (
    <div className="page-wrap">
      <div className="page-header fade-up">
        <h1 className="page-title">Live Quiz</h1>
        <p className="page-sub">Host a live, synchronized round for an existing quiz</p>
      </div>

      {!channel ? (
        <>
          {user && (
            <MyChannelsPanel
              token={token}
              link={link}
              userId={user.id}
              toast={toast}
              onRejoined={handleRejoined}
              onCopy={handleCopy}
              refreshTick={refreshTick}
            />
          )}
          <CreateChannelForm token={token} toast={toast} onCreated={handleCreated} />
        </>
      ) : (
        <HostRoom socket={socket} channel={channel} link={link} token={token} onCopy={handleCopy} toast={toast} onReset={handleReset} />
      )}
    </div>
  )
}
