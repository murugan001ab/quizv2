export function DiffBadge({ level }) {
  return <span className={`badge badge-${level}`}>{level}</span>
}

export function SubjectTag({ subject }) {
  return <span className="tag">{subject}</span>
}

export function Spinner({ sm }) {
  return <div className={`spinner ${sm ? 'spinner-sm' : ''}`} />
}

export function Loading() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '40vh' }}>
      <div className="spinner" />
    </div>
  )
}

export function EmptyState({ icon = '📭', title, sub, action }) {
  return (
    <div className="empty-state">
      <div className="icon">{icon}</div>
      <h3>{title}</h3>
      {sub && <p style={{ fontSize: '0.875rem', marginBottom: '1.5rem' }}>{sub}</p>}
      {action}
    </div>
  )
}

export function Modal({ title, onClose, children }) {
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem' }}>
          <h2 className="modal-title" style={{ margin: 0 }}>{title}</h2>
          <button className="btn btn-ghost btn-icon" onClick={onClose}>✕</button>
        </div>
        {children}
      </div>
    </div>
  )
}

export function ScheduleInfo({ start, end }) {
  const fmt = d => d ? new Date(d).toLocaleString() : '—'
  return (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: '0.8rem', color: 'var(--text3)' }}>
      <span>🗓 Start: <b style={{ color: 'var(--text2)' }}>{fmt(start)}</b></span>
      <span>⏰ End: <b style={{ color: 'var(--text2)' }}>{fmt(end)}</b></span>
    </div>
  )
}

export function QuizCard({ quiz, onClick, actions }) {
  const now = new Date()
  const start = quiz.scheduled_start ? new Date(quiz.scheduled_start) : null
  const end = quiz.scheduled_end ? new Date(quiz.scheduled_end) : null
  const isLive = (!start || now >= start) && (!end || now <= end)
  const isUpcoming = start && now < start
  const isEnded = end && now > end

  return (
    <div className={`card card-hover fade-up`} onClick={onClick} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      <div className="flex justify-between items-center">
        <DiffBadge level={quiz.difficulty} />
        {isLive && !isEnded && <span className="flex items-center gap-1" style={{ fontSize: '0.72rem', color: 'var(--accent)' }}><span className="live-dot" /> LIVE</span>}
        {isUpcoming && <span className="badge badge-blue">UPCOMING</span>}
        {isEnded && <span className="badge badge-gray">ENDED</span>}
      </div>
      <div>
        <div style={{ fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: '1.05rem', marginBottom: '0.25rem' }}>{quiz.title}</div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text3)' }}>{quiz.description}</div>
      </div>
      <div className="flex gap-1" style={{ flexWrap: 'wrap' }}>
        <SubjectTag subject={quiz.subject} />
        <SubjectTag subject={quiz.topic} />
      </div>
      <div className="flex justify-between items-center" style={{ marginTop: 'auto', paddingTop: '0.5rem', borderTop: '1px solid var(--border)' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text3)' }}>📝 {quiz.question_count} questions</span>
        {actions}
      </div>
    </div>
  )
}
