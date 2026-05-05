import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { Loading, DiffBadge } from '../components/Shared'

const KEYS = ['A', 'B', 'C', 'D']

export default function Result() {
  const { id } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.resultDetail(token, id).then(setData).finally(() => setLoading(false))
  }, [id])

  if (loading) return <Loading />
  if (!data) return null

  const pct = Math.round((data.score / data.total) * 100)
  const grade = pct >= 80 ? { label: 'Excellent!', color: 'var(--accent)', emoji: '🏆' }
    : pct >= 60 ? { label: 'Good Job!', color: 'var(--blue)', emoji: '👍' }
    : pct >= 40 ? { label: 'Keep Trying', color: 'var(--yellow)', emoji: '💪' }
    : { label: 'Needs Work', color: 'var(--red)', emoji: '📚' }

  return (
    <div className="page-wrap" style={{ maxWidth: 760 }}>
      {/* Score hero */}
      <div className="card fade-up" style={{ textAlign: 'center', padding: '2.5rem', marginBottom: '2rem', background: 'var(--card)' }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{grade.emoji}</div>
        <div style={{ fontFamily: 'var(--font-head)', fontSize: '1.5rem', fontWeight: 800, color: grade.color, marginBottom: '0.25rem' }}>
          {grade.label}
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', margin: '1.5rem 0' }}>
          <div className="score-ring" style={{ borderColor: grade.color, boxShadow: `0 0 30px ${grade.color}40` }}>
            <div className="score-num" style={{ color: grade.color }}>{pct}%</div>
            <div className="score-label">score</div>
          </div>
        </div>
        <div style={{ color: 'var(--text2)', fontSize: '1rem' }}>
          You scored <b style={{ color: 'var(--text)' }}>{data.score}</b> out of <b style={{ color: 'var(--text)' }}>{data.total}</b> questions
        </div>
        <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text3)' }}>
          Submitted: {new Date(data.submitted_at).toLocaleString()}
        </div>
      </div>

      {/* Question review */}
      <div className="fade-up-1" style={{ marginBottom: '1rem' }}>
        <h2 style={{ fontFamily: 'var(--font-head)', fontWeight: 700, marginBottom: '1rem' }}>Question Review</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {data.questions.map((q, i) => {
            const chosen = data.answers[q.id]
            const correct = q.correct_option
            const isRight = chosen === correct

            return (
              <div key={q.id} className="card">
                <div className="flex justify-between items-center" style={{ marginBottom: '0.75rem' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text3)', fontWeight: 600 }}>Q{i + 1}</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: isRight ? 'var(--accent)' : 'var(--red)' }}>
                    {isRight ? '✓ Correct' : '✗ Wrong'}
                  </span>
                </div>
                <p style={{ fontWeight: 500, marginBottom: '0.875rem', lineHeight: 1.6 }}>{q.text}</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {q.options.map((opt, j) => {
                    const isChosen = chosen === j
                    const isCor = correct === j
                    const cls = isCor ? 'correct' : isChosen && !isCor ? 'wrong' : ''
                    return (
                      <div key={j} className={`option-btn ${cls}`} style={{ cursor: 'default' }}>
                        <span className={`option-key`}>{KEYS[j]}</span>
                        {opt}
                        {isCor && <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--accent2)', fontWeight: 600 }}>✓ Correct</span>}
                        {isChosen && !isCor && <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--red)', fontWeight: 600 }}>Your answer</span>}
                      </div>
                    )
                  })}
                </div>
                {q.explanation && (
                  <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'var(--bg3)', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', color: 'var(--text2)', borderLeft: '3px solid var(--accent)' }}>
                    💡 {q.explanation}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      <div className="flex gap-2 fade-up-2" style={{ marginTop: '1.5rem' }}>
        <button className="btn btn-ghost" onClick={() => navigate('/results')}>← All Results</button>
        <button className="btn btn-primary" onClick={() => navigate('/quizzes')}>Take Another Quiz</button>
      </div>
    </div>
  )
}
