import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { Loading, DiffBadge, EmptyState } from '../components/Shared'

export default function Results() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.myResults(token).then(setResults).finally(() => setLoading(false))
  }, [token])

  if (loading) return <Loading />

  const avgScore = results.length
    ? Math.round(results.reduce((a, r) => a + (r.score / r.total) * 100, 0) / results.length)
    : 0
  const best = results.length
    ? Math.round(Math.max(...results.map(r => (r.score / r.total) * 100)))
    : 0

  return (
    <div className="page-wrap">
      <div className="page-header fade-up">
        <h1 className="page-title">My Results</h1>
        <p className="page-sub">Review your quiz history and scores</p>
      </div>

      {results.length > 0 && (
        <div className="stats-grid fade-up-1">
          <div className="stat-card">
            <div className="stat-label">Total Attempts</div>
            <div className="stat-value">{results.length}</div>
            <div className="stat-sub">Quizzes submitted</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Avg. Score</div>
            <div className="stat-value">{avgScore}<span style={{ fontSize: '1rem', color: 'var(--text3)' }}>%</span></div>
            <div className="stat-sub">Across all tests</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Best Score</div>
            <div className="stat-value" style={{ color: 'var(--accent)' }}>{best}<span style={{ fontSize: '1rem', color: 'var(--text3)' }}>%</span></div>
            <div className="stat-sub">Personal best</div>
          </div>
        </div>
      )}

      {results.length === 0
        ? <EmptyState icon="🏆" title="No results yet" sub="Take a quiz to see your results here." action={
            <button className="btn btn-primary" onClick={() => navigate('/quizzes')}>Browse Quizzes →</button>
          } />
        : (
          <div className="card fade-up-2">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Quiz</th>
                    <th>Difficulty</th>
                    <th>Score</th>
                    <th>Pct.</th>
                    <th>Submitted</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {results.map(r => {
                    const pct = Math.round((r.score / r.total) * 100)
                    const color = pct >= 80 ? 'var(--accent)' : pct >= 60 ? 'var(--blue)' : pct >= 40 ? 'var(--yellow)' : 'var(--red)'
                    return (
                      <tr key={r.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/results/${r.id}`)}>
                        <td style={{ color: 'var(--text)', fontWeight: 500 }}>{r.quiz_title}</td>
                        <td><DiffBadge level={r.difficulty} /></td>
                        <td style={{ fontFamily: 'var(--font-head)', fontWeight: 700 }}>{r.score}/{r.total}</td>
                        <td>
                          <span style={{ fontFamily: 'var(--font-head)', fontWeight: 700, color }}>{pct}%</span>
                        </td>
                        <td>{new Date(r.submitted_at).toLocaleDateString()}</td>
                        <td>
                          <button className="btn btn-ghost btn-sm" onClick={e => { e.stopPropagation(); navigate(`/results/${r.id}`) }}>
                            Review →
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )
      }
    </div>
  )
}
