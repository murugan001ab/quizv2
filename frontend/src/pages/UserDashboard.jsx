import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { Loading, QuizCard, EmptyState } from '../components/Shared'

export default function UserDashboard() {
  const { token, user } = useAuth()
  const navigate = useNavigate()
  const [quizzes, setQuizzes] = useState([])
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.userQuizzes(token), api.myResults(token)])
      .then(([q, r]) => { setQuizzes(q); setResults(r) })
      .finally(() => setLoading(false))
  }, [token])

  if (loading) return <Loading />

  const completed = results.length
  const avgScore = results.length
    ? Math.round(results.reduce((a, r) => a + (r.score / r.total) * 100, 0) / results.length)
    : 0
  const available = quizzes.length

  return (
    <div className="page-wrap">
      <div className="page-header fade-up">
        <h1 className="page-title">Hey, {user?.username} 👋</h1>
        <p className="page-sub">Ready to test your knowledge today?</p>
      </div>

      <div className="stats-grid fade-up-1">
        <div className="stat-card">
          <div className="stat-label">Available Quizzes</div>
          <div className="stat-value">{available}</div>
          <div className="stat-sub">Ready to take</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Completed</div>
          <div className="stat-value">{completed}</div>
          <div className="stat-sub">Tests submitted</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg. Score</div>
          <div className="stat-value">{avgScore}<span style={{ fontSize: '1rem', color: 'var(--text3)' }}>%</span></div>
          <div className="stat-sub">Across all tests</div>
        </div>
      </div>

      <div className="fade-up-2">
        <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
          <h2 style={{ fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: '1.1rem' }}>Available Tests</h2>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/quizzes')}>View All →</button>
        </div>
        {quizzes.length === 0
          ? <EmptyState icon="📭" title="No quizzes yet" sub="Check back later when tests are added." />
          : <div className="quiz-grid">
              {quizzes.slice(0, 6).map((q, i) => (
                <QuizCard key={q.id} quiz={q}
                  onClick={() => navigate(`/quiz/${q.id}`)}
                  actions={<button className="btn btn-primary btn-sm" onClick={e => { e.stopPropagation(); navigate(`/quiz/${q.id}`) }}>Take Test →</button>}
                />
              ))}
            </div>
        }
      </div>
    </div>
  )
}
