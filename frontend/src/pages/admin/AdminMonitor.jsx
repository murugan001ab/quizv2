import { useEffect, useState, useRef } from 'react'
import { useAuth } from '../../context/AuthContext'

const MAX_EVENTS = 50

function EventCard({ ev, i }) {
  const isStart = ev.type === 'quiz_started'
  const color = isStart ? 'var(--blue)' : 'var(--accent)'
  const bg = isStart ? 'var(--blue-dim)' : 'var(--accent-dim)'
  const border = isStart ? 'rgba(96,165,250,0.3)' : 'rgba(110,231,183,0.3)'
  const icon = isStart ? '▶' : '✓'

  return (
    <div className="fade-up" style={{
      animationDelay: `${i * 0.03}s`,
      display: 'flex', gap: '0.75rem', alignItems: 'flex-start',
      padding: '0.875rem 1rem',
      background: 'var(--bg3)',
      border: '1px solid var(--border)',
      borderLeft: `3px solid ${color}`,
      borderRadius: 'var(--radius-sm)',
    }}>
      <span style={{
        width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
        background: bg, border: `1px solid ${border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '0.7rem', fontWeight: 700, color,
      }}>{icon}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', flexWrap: 'wrap' }}>
          <div>
            <span style={{ fontWeight: 600, color: 'var(--text)', fontSize: '0.875rem' }}>{ev.user}</span>
            <span style={{ color: 'var(--text3)', fontSize: '0.8rem', margin: '0 0.375rem' }}>
              {isStart ? 'started' : 'submitted'}
            </span>
            <span style={{ color: 'var(--text2)', fontSize: '0.875rem', fontWeight: 500 }}>{ev.quiz_title}</span>
          </div>
          <span style={{ fontSize: '0.72rem', color: 'var(--text3)', flexShrink: 0 }}>
            {new Date(ev.ts).toLocaleTimeString()}
          </span>
        </div>
        {!isStart && ev.score != null && (
          <div style={{ marginTop: '0.375rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <span style={{
              fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: '0.875rem',
              color: (ev.score / ev.total) >= 0.8 ? 'var(--accent)'
                : (ev.score / ev.total) >= 0.6 ? 'var(--blue)'
                : (ev.score / ev.total) >= 0.4 ? 'var(--yellow)' : 'var(--red)',
            }}>
              {ev.score}/{ev.total}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text3)' }}>
              ({Math.round((ev.score / ev.total) * 100)}%)
            </span>
          </div>
        )}
        {ev.difficulty && (
          <span style={{
            display: 'inline-block', marginTop: '0.25rem',
            padding: '0.1rem 0.4rem', borderRadius: 4, fontSize: '0.68rem', fontWeight: 600,
            background: ev.difficulty === 'easy' ? 'rgba(52,211,153,0.1)' : ev.difficulty === 'hard' ? 'var(--red-dim)' : 'var(--yellow-dim)',
            color: ev.difficulty === 'easy' ? 'var(--accent2)' : ev.difficulty === 'hard' ? 'var(--red)' : 'var(--yellow)',
          }}>{ev.difficulty}</span>
        )}
      </div>
    </div>
  )
}

function LiveCounter({ count }) {
  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: '0.625rem',
      padding: '0.375rem 0.875rem',
      background: count > 0 ? 'var(--accent-dim)' : 'var(--bg3)',
      border: `1px solid ${count > 0 ? 'rgba(110,231,183,0.3)' : 'var(--border)'}`,
      borderRadius: 999,
      fontSize: '0.875rem', fontWeight: 600,
      color: count > 0 ? 'var(--accent)' : 'var(--text3)',
    }}>
      {count > 0 && <span className="live-dot" />}
      {count} live
    </div>
  )
}

export default function AdminMonitor() {
  const { token } = useAuth()
  const [events, setEvents] = useState([])
  const [connected, setConnected] = useState(false)
  const [liveCount, setLiveCount] = useState(0)
  const [error, setError] = useState('')
  const wsRef = useRef(null)
  const feedRef = useRef(null)

  const addEvent = (ev) => {
    const enriched = { ...ev, ts: ev.ts || new Date().toISOString() }
    setEvents(prev => [enriched, ...prev].slice(0, MAX_EVENTS))
    // track live count
    if (ev.type === 'quiz_started') setLiveCount(c => c + 1)
    if (ev.type === 'quiz_submitted') setLiveCount(c => Math.max(0, c - 1))
  }

  const connect = () => {
    if (wsRef.current) wsRef.current.close()
    setError('')

    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`ws://localhost:8000/ws/admin?token=${token}`)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => {
      setConnected(false)
      // auto-reconnect after 3s
      setTimeout(() => { if (wsRef.current === ws) connect() }, 3000)
    }
    ws.onerror = () => setError('WebSocket error — retrying...')
    ws.onmessage = (e) => {
      try { addEvent(JSON.parse(e.data)) }
      catch { /* ignore malformed */ }
    }
  }

  useEffect(() => {
    connect()
    return () => { if (wsRef.current) { wsRef.current.onclose = null; wsRef.current.close() } }
  }, [token])

  const clear = () => setEvents([])

  return (
    <div className="page-wrap">
      <div className="page-header fade-up">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="page-title">Live Monitor</h1>
            <p className="page-sub">Real-time quiz activity via WebSocket</p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <LiveCounter count={liveCount} />
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.375rem',
              padding: '0.375rem 0.875rem',
              background: connected ? 'rgba(52,211,153,0.1)' : 'var(--red-dim)',
              border: `1px solid ${connected ? 'rgba(52,211,153,0.3)' : 'rgba(248,113,113,0.3)'}`,
              borderRadius: 999, fontSize: '0.8rem', fontWeight: 600,
              color: connected ? 'var(--accent2)' : 'var(--red)',
            }}>
              {connected ? <>● Connected</> : <>○ Disconnected</>}
            </span>
            <button className="btn btn-ghost btn-sm" onClick={connect}>Reconnect</button>
            {events.length > 0 && <button className="btn btn-ghost btn-sm" onClick={clear}>Clear</button>}
          </div>
        </div>
      </div>

      {error && (
        <div style={{
          padding: '0.75rem 1rem', background: 'var(--red-dim)',
          border: '1px solid rgba(248,113,113,0.3)', borderRadius: 'var(--radius-sm)',
          color: 'var(--red)', fontSize: '0.875rem', marginBottom: '1rem',
        }}>{error}</div>
      )}

      {/* Legend */}
      <div className="fade-up-1" style={{ display: 'flex', gap: '1rem', marginBottom: '1.25rem', fontSize: '0.8rem', color: 'var(--text3)', flexWrap: 'wrap' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--blue)', display: 'inline-block' }} />
          quiz_started
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--accent)', display: 'inline-block' }} />
          quiz_submitted
        </span>
        <span style={{ marginLeft: 'auto' }}>Showing last {MAX_EVENTS} events</span>
      </div>

      {/* Event feed */}
      <div ref={feedRef} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {events.length === 0 ? (
          <div style={{
            textAlign: 'center', padding: '5rem 2rem',
            background: 'var(--card)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius)', color: 'var(--text3)',
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem', opacity: 0.4 }}>📡</div>
            <div style={{ fontSize: '1rem', color: 'var(--text2)', marginBottom: '0.375rem' }}>
              {connected ? 'Waiting for activity…' : 'Connecting…'}
            </div>
            <div style={{ fontSize: '0.8rem' }}>Events will appear here as users start and submit quizzes.</div>
          </div>
        ) : (
          events.map((ev, i) => <EventCard key={`${ev.ts}-${i}`} ev={ev} i={i} />)
        )}
      </div>
    </div>
  )
}
