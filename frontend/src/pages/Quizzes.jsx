import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { Loading, QuizCard, EmptyState } from '../components/Shared'

const SUBJECTS = ['All', 'Tamil', 'Science', 'Physics', 'Maths', 'Biology', 'Chemistry']
const DIFFS = ['All', 'easy', 'medium', 'hard']

export default function Quizzes() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [quizzes, setQuizzes] = useState([])
  const [loading, setLoading] = useState(true)
  const [subject, setSubject] = useState('All')
  const [diff, setDiff] = useState('All')

  const load = () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (diff !== 'All') params.set('difficulty', diff)
    if (subject !== 'All') params.set('subject', subject)
    const q = params.toString() ? `?${params}` : ''
    api.userQuizzes(token, q).then(setQuizzes).finally(() => setLoading(false))
  }

  useEffect(load, [diff, subject])

  return (
    <div className="page-wrap">
      <div className="page-header fade-up">
        <h1 className="page-title">Browse Quizzes</h1>
        <p className="page-sub">Filter by subject or difficulty</p>
      </div>

      <div className="flex gap-2 fade-up-1" style={{ marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <div className="input-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.5rem' }}>
          <label className="input-label" style={{ whiteSpace: 'nowrap' }}>Subject</label>
          <select className="input" value={subject} onChange={e => setSubject(e.target.value)} style={{ width: 'auto' }}>
            {SUBJECTS.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div className="input-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.5rem' }}>
          <label className="input-label" style={{ whiteSpace: 'nowrap' }}>Difficulty</label>
          <select className="input" value={diff} onChange={e => setDiff(e.target.value)} style={{ width: 'auto' }}>
            {DIFFS.map(d => <option key={d}>{d}</option>)}
          </select>
        </div>
      </div>

      {loading ? <Loading /> : quizzes.length === 0
        ? <EmptyState icon="🔍" title="No quizzes found" sub="Try a different filter." />
        : <div className="quiz-grid fade-up-2">
            {quizzes.map(q => (
              <QuizCard key={q.id} quiz={q}
                onClick={() => navigate(`/quiz/${q.id}`)}
                actions={<button className="btn btn-primary btn-sm" onClick={e => { e.stopPropagation(); navigate(`/quiz/${q.id}`) }}>Take Test →</button>}
              />
            ))}
          </div>
      }
    </div>
  )
}
