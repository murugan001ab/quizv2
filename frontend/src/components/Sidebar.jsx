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
  { to: '/account', icon: '👤', label: 'Account' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const { pathname } = useLocation()
  const nav = user?.is_admin ? adminNav : userNav

  return (
    <aside className="fixed left-4 top-4 bottom-4 w-64 z-40 flex flex-col glass-panel p-4 animate-fade-up">
      <div className="px-2 pt-2 pb-5 border-b border-white/10 mb-4">
        <h1 className="font-head font-extrabold text-xl tracking-tight text-white">
          Quiz<span className="text-accent-400">Master</span>
        </h1>
        <div className="text-xs text-white/40 mt-1">
          {user?.is_admin ? '🛡 Admin Panel' : '🎓 Student Panel'}
        </div>
      </div>

      <nav className="flex-1 flex flex-col gap-1">
        {nav.map(item => {
          const active = pathname === item.to || (item.to !== '/' && pathname.startsWith(item.to) && item.to.length > 7)
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm font-medium transition-all duration-200
                ${active
                  ? 'bg-white/[0.09] text-white shadow-inner-glass border border-white/10'
                  : 'text-white/50 hover:text-white/85 hover:bg-white/[0.05] border border-transparent'}`}
            >
              <span className="text-base w-5 text-center">{item.icon}</span>
              {item.label}
            </Link>
          )
        })}
      </nav>

      <div className="pt-4 border-t border-white/10">
        <div className="flex items-center gap-2.5 mb-3">
          <Link
            to="/account"
            className="w-9 h-9 rounded-full shrink-0 overflow-hidden bg-white/5 border border-white/10 flex items-center justify-center"
          >
            {user?.profile_url ? (
              <img src={user.profile_url} alt="" className="w-full h-full object-cover" />
            ) : (
              <span className="font-head font-bold text-sm text-white/50">
                {(user?.username || '?').slice(0, 1).toUpperCase()}
              </span>
            )}
          </Link>
          <div className="text-xs text-white/40 min-w-0">
            <div className="font-semibold text-white/75 truncate">{user?.username}</div>
            <div className="truncate">{user?.email}</div>
          </div>
        </div>
        <button className="btn btn-ghost w-full justify-start gap-2" onClick={logout}>
          <span>↩</span> Logout
        </button>
      </div>
    </aside>
  )
}
