export function DiffBadge({ level }) {
  const cls = { easy: 'badge-easy', medium: 'badge-medium', hard: 'badge-hard' }[level] || 'badge-gray'
  return <span className={cls}>{level}</span>
}

export function SubjectTag({ subject }) {
  if (!subject) return null
  return <span className="tag">{subject}</span>
}

export function Spinner({ sm }) {
  return <div className={`spinner ${sm ? 'spinner-sm' : ''}`} />
}

export function Loading() {
  return (
    <div className="flex items-center justify-center h-[40vh]">
      <div className="spinner" />
    </div>
  )
}

export function EmptyState({ icon = '📭', title, sub, action }) {
  return (
    <div className="glass-panel flex flex-col items-center justify-center text-center py-16 px-6 fade-up">
      <div className="text-4xl mb-4 opacity-80">{icon}</div>
      <h3 className="font-head font-bold text-lg text-white/90">{title}</h3>
      {sub && <p className="text-sm text-white/40 mt-2 mb-6 max-w-xs">{sub}</p>}
      {action}
    </div>
  )
}

export function Modal({ title, onClose, children }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-space-950/70 backdrop-blur-md p-4 animate-[fadeUp_0.25s_ease-out]"
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <div className="glass-panel w-full max-w-lg max-h-[85vh] overflow-y-auto p-7 shadow-glass-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="font-head font-bold text-xl text-white/90">{title}</h2>
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
    <div className="flex gap-4 flex-wrap text-xs text-white/40">
      <span>🗓 Start: <b className="text-white/60 font-medium">{fmt(start)}</b></span>
      <span>⏰ End: <b className="text-white/60 font-medium">{fmt(end)}</b></span>
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
    <div
      onClick={onClick}
      className="glass-panel glass-hover fade-up cursor-pointer flex flex-col gap-3 p-5"
    >
      <div className="flex justify-between items-center">
        <DiffBadge level={quiz.difficulty} />
        {isLive && !isEnded && (
          <span className="flex items-center gap-1.5 text-[0.7rem] font-medium text-accent-300">
            <span className="live-dot" /> LIVE
          </span>
        )}
        {isUpcoming && <span className="badge-blue">UPCOMING</span>}
        {isEnded && <span className="badge-gray">ENDED</span>}
      </div>

      <div>
        <div className="font-head font-bold text-[1.05rem] text-white/90 mb-1">{quiz.title}</div>
        <div className="text-sm text-white/40 line-clamp-2">{quiz.description}</div>
      </div>

      <div className="flex gap-1.5 flex-wrap">
        <SubjectTag subject={quiz.subject} />
        <SubjectTag subject={quiz.topic} />
      </div>

      <div className="flex justify-between items-center mt-auto pt-3 border-t border-white/10">
        <span className="text-xs text-white/40">📝 {quiz.question_count} questions</span>
        {actions}
      </div>
    </div>
  )
}
