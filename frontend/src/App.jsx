import { Routes, Route, Navigate, useLocation } from 'react-router-dom'

import { AuthProvider, useAuth } from './context/AuthContext'
import { ToastProvider } from './context/ToastContext'
import { DataProvider } from './context/DataContext'

import Sidebar from './components/Sidebar'
import MobileHeader from './components/MobileHeader'
import BottomNav from './components/BottomNav'
import { Loading } from './components/Shared'

import Login from './pages/Login'
import Account from './pages/Account'
import UserDashboard from './pages/UserDashboard'
import Quizzes from './pages/Quizzes'
import TakeQuiz from './pages/TakeQuiz'
import Result from './pages/Result'
import Results from './pages/Results'
import LiveQuiz from './pages/LiveQuiz'
import ProblemList from './pages/Problems/ProblemList'
import ProblemSolve from './pages/Problems/ProblemSolve'

import AdminDashboard from './pages/admin/AdminDashboard'
import AdminQuizzes from './pages/admin/AdminQuizzes'
import AdminUsers from './pages/admin/AdminUsers'
import AdminLive from './pages/admin/AdminLive'
import AdminProblems from './pages/admin/AdminProblems'
import ProblemForm from './pages/admin/ProblemForm'
import Register from './pages/Register'

function AppShell({ children }) {
  return (
    <div className="min-h-screen">
      <Sidebar />
      <MobileHeader />

      <main className="min-h-screen px-4 pt-[4.5rem] pb-24 md:pl-[17.5rem] md:pr-4 md:pt-4 md:pb-4">
        {children}
      </main>

      <BottomNav />
    </div>
  )
}


function RequireAuth({ children, adminOnly = false }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <Loading />
  }

  if (!user) {
    // Remember where they were headed (e.g. a shared live-quiz link) so
    // Login can send them back here instead of to the default dashboard.
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  if (adminOnly && !user.is_admin) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}


function RootRedirect() {
  const { user, loading } = useAuth()

  if (loading) {
    return <Loading />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return (
    <Navigate
      to={user.is_admin ? '/admin' : '/dashboard'}
      replace
    />
  )
}


export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <DataProvider>
          <Routes>

            {/* ================= PUBLIC ================= */}

            <Route
              path="/login"
              element={<Login />}
            />
            {/* <Route
              path="/register"
              element={<Register/>}
              /> */}

            {/* ================= USER ================= */}

            <Route
              path="/dashboard"
              element={
                <RequireAuth>
                  <AppShell>
                    <UserDashboard />
                  </AppShell>
                </RequireAuth>
              }
            />

            <Route
              path="/quizzes"
              element={
                <RequireAuth>
                  <AppShell>
                    <Quizzes />
                  </AppShell>
                </RequireAuth>
              }
            />

            <Route
              path="/quiz/:id"
              element={
                <RequireAuth>
                  <AppShell>
                    <TakeQuiz />
                  </AppShell>
                </RequireAuth>
              }
            />

            <Route
              path="/results"
              element={
                <RequireAuth>
                  <AppShell>
                    <Results />
                  </AppShell>
                </RequireAuth>
              }
            />

            <Route
              path="/results/:id"
              element={
                <RequireAuth>
                  <AppShell>
                    <Result />
                  </AppShell>
                </RequireAuth>
              }
            />

            <Route
              path="/live"
              element={
                <RequireAuth>
                  <AppShell>
                    <LiveQuiz />
                  </AppShell>
                </RequireAuth>
              }
            />
            <Route
              path="/live/:code/:link_token"
              element={
                <RequireAuth>
                  <AppShell>
                    <LiveQuiz />
                  </AppShell>
                </RequireAuth>
              }
            />


            <Route
              path="/problems"
              element={
                <RequireAuth>
                  <AppShell>
                    <ProblemList />
                  </AppShell>
                </RequireAuth>
              }
            />

            <Route
              path="/problems/:id"
              element={
                <RequireAuth>
                  <ProblemSolve />
                </RequireAuth>
              }
            />

            <Route
              path="/account"
              element={
                <RequireAuth>
                  <AppShell>
                    <Account />
                  </AppShell>
                </RequireAuth>
              }
            />

            {/* <Route
              path="/code"
              element={
                <RequireAuth>
                  <AppShell>
                    <CodeEditor/>
                  </AppShell>
                </RequireAuth>
              }
            /> */}


            {/* ================= ADMIN ================= */}

            <Route
              path="/admin"
              element={
                <RequireAuth adminOnly>
                  <AppShell>
                    <AdminDashboard />
                  </AppShell>
                </RequireAuth>
              }
            />

            <Route
              path="/admin/quizzes"
              element={
                <RequireAuth adminOnly>
                  <AppShell>
                    <AdminQuizzes />
                  </AppShell>
                </RequireAuth>
              }
            />
            <Route
              path="/admin/problems"
              element={
                <RequireAuth adminOnly>
                  <AppShell>
                    <AdminProblems />
                  </AppShell>
                </RequireAuth>
              }
            />
            <Route
              path="/admin/problems/new"
              element={
                <RequireAuth adminOnly>
                  <AppShell>
                    <ProblemForm />
                  </AppShell>
                </RequireAuth>
              }
            />
            <Route
              path="/admin/problems/:id/edit"
              element={
                <RequireAuth adminOnly>
                  <AppShell>
                    <ProblemForm />
                  </AppShell>
                </RequireAuth>
              }
            />
            <Route
              path="/admin/users"
              element={
                <RequireAuth adminOnly>
                  <AppShell>
                    <AdminUsers />
                  </AppShell>
                </RequireAuth>
              }
            />

            <Route
              path="/admin/live"
              element={
                <RequireAuth adminOnly>
                  <AppShell>
                    <AdminLive />
                  </AppShell>
                </RequireAuth>
              }
            />


            {/* ================= FALLBACK ================= */}

            <Route
              path="*"
              element={<RootRedirect />}
            />

          </Routes>
        </DataProvider>
      </ToastProvider>
    </AuthProvider>
  )
}