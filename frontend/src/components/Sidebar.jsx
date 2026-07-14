import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const userNav = [
  { to: '/dashboard', icon: '⊞', label: 'Dashboard' },
  { to: '/quizzes', icon: '📋', label: 'Quizzes' },
  { to: '/live', icon: '⚡', label: 'Live Quiz' },
  { to: '/results', icon: '🏆', label: 'Results' },
  { to: '/account', icon: '👤', label: 'Account' },
]

const adminNav = [
  { to: '/admin', icon: '⊞', label: 'Dashboard' },
  { to: '/admin/quizzes', icon: '📋', label: 'Manage Quizzes' },
  { to: '/admin/users', icon: '👥', label: 'Users' },
  { to: '/admin/live', icon: '⚡', label: 'Live Quiz' },
  // { to: '/admin/monitor', icon: '📡', label: 'Live Monitor' },
  { to: '/account', icon: '👤', label: 'Account' },
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', marginBottom: '0.75rem' }}>
          <Link to="/account" style={{
            width: 36, height: 36, borderRadius: '50%', flexShrink: 0, overflow: 'hidden',
            background: 'var(--bg3)', border: '1px solid var(--border)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {user?.profile_url ? (
              <img src={user.profile_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            ) : (
              <span style={{ fontFamily: 'var(--font-head)', fontWeight: 700, fontSize: '0.9rem', color: 'var(--text3)' }}>
                {(user?.username || '?').slice(0, 1).toUpperCase()}
              </span>
            )}
          </Link>
          <div style={{ fontSize: '0.8rem', color: 'var(--text3)', minWidth: 0 }}>
            <div style={{ fontWeight: 600, color: 'var(--text2)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{user?.username}</div>
            <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{user?.email}</div>
          </div>
        </div>
        <button className="btn btn-ghost w-full" onClick={logout} style={{ justifyContent: 'flex-start', gap: '0.5rem' }}>
          <span>↩</span> Logout
        </button>
      </div>
    </aside>
  )
}
