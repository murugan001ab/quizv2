import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ToastProvider } from './context/ToastContext'
import { DataProvider } from './context/DataContext'
import Sidebar from './components/Sidebar'
import { Loading } from './components/Shared'

import Login from './pages/Login'
import Register from './pages/Register'
import UserDashboard from './pages/UserDashboard'
import Quizzes from './pages/Quizzes'
import TakeQuiz from './pages/TakeQuiz'
import Result from './pages/Result'
import Results from './pages/Results'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminQuizzes from './pages/admin/AdminQuizzes'
import AdminUsers from './pages/admin/AdminUsers'
import AdminMonitor from './pages/admin/AdminMonitor'

function AppShell({ children }) {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="app-main">{children}</main>
    </div>
  )
}

function RequireAuth({ children, adminOnly = false }) {
  const { user, loading } = useAuth()
  if (loading) return <Loading />
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && !user.is_admin) return <Navigate to="/dashboard" replace />
  return children
}

function RootRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <Loading />
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={user.is_admin ? '/admin' : '/dashboard'} replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <DataProvider>
            <Routes>
              {/* Public */}
              <Route path="/login"    element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* User routes */}
              <Route path="/dashboard" element={
                <RequireAuth><AppShell><UserDashboard /></AppShell></RequireAuth>
              } />
              <Route path="/quizzes" element={
                <RequireAuth><AppShell><Quizzes /></AppShell></RequireAuth>
              } />
              <Route path="/quiz/:id" element={
                <RequireAuth><AppShell><TakeQuiz /></AppShell></RequireAuth>
              } />
              <Route path="/results" element={
                <RequireAuth><AppShell><Results /></AppShell></RequireAuth>
              } />
              <Route path="/results/:id" element={
                <RequireAuth><AppShell><Result /></AppShell></RequireAuth>
              } />

              {/* Admin routes */}
              <Route path="/admin" element={
                <RequireAuth adminOnly><AppShell><AdminDashboard /></AppShell></RequireAuth>
              } />
              <Route path="/admin/quizzes" element={
                <RequireAuth adminOnly><AppShell><AdminQuizzes /></AppShell></RequireAuth>
              } />
              <Route path="/admin/users" element={
                <RequireAuth adminOnly><AppShell><AdminUsers /></AppShell></RequireAuth>
              } />
              <Route path="/admin/monitor" element={
                <RequireAuth adminOnly><AppShell><AdminMonitor /></AppShell></RequireAuth>
              } />

              {/* Fallback */}
              <Route path="*" element={<RootRedirect />} />
            </Routes>
          </DataProvider>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
