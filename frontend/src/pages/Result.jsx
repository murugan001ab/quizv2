import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { Loading } from '../components/Shared'
import QuestionText from '../components/QuestionText'

const KEYS = ['A', 'B', 'C', 'D']

export default function Result() {
  const { id } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState('')

  useEffect(() => {
    api.resultDetail(token, id)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <Loading />

  if (error || !data) return (
    <div className="page-wrap">
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>❌</div>
        <h2 style={{ fontFamily: 'var(--font-head)', marginBottom: '0.5rem' }}>Result not found</h2>
        <p style={{ color: 'var(--text3)', marginBottom: '1.5rem' }}>{error}</p>
        <button className="btn btn-ghost" onClick={() => navigate('/results')}>← Back to Results</button>
      </div>
    </div>
  )

  // Normalise string keys → number keys
  const answers = {}
  for (const [k, v] of Object.entries(data.answers || {})) {
    answers[Number(k)] = v
  }

  const pct = data.total > 0 ? Math.round((data.score / data.total) * 100) : 0
  const grade = pct >= 80 ? { label: 'Excellent!', color: 'var(--accent)',  emoji: '🏆' }
    : pct >= 60          ? { label: 'Good Job!',   color: 'var(--blue)',    emoji: '👍' }
    : pct >= 40          ? { label: 'Keep Trying',  color: 'var(--yellow)', emoji: '💪' }
    :                      { label: 'Needs Work',   color: 'var(--red)',    emoji: '📚' }

  return (
    <div className="page-wrap" style={{ maxWidth: 760 }}>

      {/* ── Score hero ── */}
      <div className="card fade-up" style={{ textAlign: 'center', padding: '2.5rem', marginBottom: '2rem' }}>
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

      {/* ── Question review ── */}
      <div className="fade-up-1" style={{ marginBottom: '1rem' }}>
        <h2 style={{ fontFamily: 'var(--font-head)', fontWeight: 700, marginBottom: '1rem' }}>Question Review</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {data.questions.map((q, i) => {
            const chosen  = answers[q.id]
            const correct = q.correct_option
            const skipped = chosen === undefined
            const isRight = !skipped && chosen === correct

            return (
              <div key={q.id} className="card">
                {/* Header row */}
                <div className="flex justify-between items-center" style={{ marginBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text3)', fontWeight: 600 }}>Q{i + 1}</span>
                    {q.year && (
                      <span style={{
                        fontSize: '0.68rem', fontWeight: 600, padding: '0.1rem 0.45rem',
                        borderRadius: 4, background: 'var(--accent-dim)', color: 'var(--accent)',
                      }}>{q.year}</span>
                    )}
                  </div>
                  <span style={{
                    fontSize: '0.75rem', fontWeight: 700,
                    color: skipped ? 'var(--text3)' : isRight ? 'var(--accent)' : 'var(--red)',
                  }}>
                    {skipped ? '— Skipped' : isRight ? '✓ Correct' : '✗ Wrong'}
                  </span>
                </div>

                {/* ✅ Structured question renderer */}
                <div style={{ marginBottom: '0.875rem' }}>
                  <QuestionText text={q.text} />
                </div>

                {/* Options */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {q.options.map((opt, j) => {
                    const isChosen  = chosen === j
                    const isCorrect = correct === j
                    const cls = isCorrect ? 'correct' : (isChosen && !isCorrect) ? 'wrong' : ''
                    return (
                      <div key={j} className={`option-btn ${cls}`} style={{ cursor: 'default' }}>
                        <span className="option-key">{KEYS[j]}</span>
                        <span style={{ flex: 1, lineHeight: 1.5 }}>{opt}</span>
                        {isCorrect && (
                          <span style={{ marginLeft: 'auto', fontSize: '0.72rem', color: 'var(--accent2)', fontWeight: 700, whiteSpace: 'nowrap' }}>
                            ✓ Correct
                          </span>
                        )}
                        {isChosen && !isCorrect && (
                          <span style={{ marginLeft: 'auto', fontSize: '0.72rem', color: 'var(--red)', fontWeight: 700, whiteSpace: 'nowrap' }}>
                            Your answer
                          </span>
                        )}
                      </div>
                    )
                  })}
                </div>

                {/* Explanation */}
                {q.explanation && (
                  <div style={{
                    marginTop: '0.875rem', padding: '0.75rem',
                    background: 'var(--bg3)', borderRadius: 'var(--radius-sm)',
                    fontSize: '0.85rem', color: 'var(--text2)',
                    borderLeft: '3px solid var(--accent)', lineHeight: 1.6,
                  }}>
                    💡 {q.explanation}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Footer ── */}
      <div className="flex gap-2 fade-up-2" style={{ marginTop: '1.5rem' }}>
        <button className="btn btn-ghost"   onClick={() => navigate('/results')}>← All Results</button>
        <button className="btn btn-primary" onClick={() => navigate('/quizzes')}>Take Another Quiz</button>
      </div>
    </div>
  )
}
