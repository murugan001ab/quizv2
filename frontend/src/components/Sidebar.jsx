import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const userNav = [
  { to: '/dashboard', icon: '⊞', label: 'Dashboard' },
  { to: '/quizzes', icon: '📋', label: 'Quizzes' },
  { to: '/results', icon: '🏆', label: 'Results' },
]

const adminNav = [
  { to: '/admin', icon: '⊞', label: 'Dashboard' },
  { to: '/admin/quizzes', icon: '📋', label: 'Manage Quizzes' },
  { to: '/admin/users', icon: '👥', label: 'Users' },
  { to: '/admin/monitor', icon: '📡', label: 'Live Monitor' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const { pathname } = useLocation()
  const nav = user?.is_admin ? adminNav : userNav

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h1>Quiz<span>Master</span></h1>
        <div style={{ fontSize: '0.75rem', color: 'var(--text3)', marginTop: '0.25rem' }}>
          {user?.is_admin ? '🛡 Admin Panel' : '🎓 Student Panel'}
        </div>
      </div>

      <nav style={{ flex: 1 }}>
        {nav.map(item => (
          <Link
            key={item.to}
            to={item.to}
            className={`nav-item ${pathname === item.to || (item.to !== '/' && pathname.startsWith(item.to) && item.to.length > 7) ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div style={{ fontSize: '0.8rem', color: 'var(--text3)', marginBottom: '0.75rem' }}>
          <div style={{ fontWeight: 600, color: 'var(--text2)' }}>{user?.username}</div>
          <div>{user?.email}</div>
        </div>
        <button className="btn btn-ghost w-full" onClick={logout} style={{ justifyContent: 'flex-start', gap: '0.5rem' }}>
          <span>↩</span> Logout
        </button>
      </div>
    </aside>
  )
}
