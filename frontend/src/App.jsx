import { Navigate, Route, Routes } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import TeacherDashboard from './pages/TeacherDashboard'
import StudentDashboard from './pages/StudentDashboard'
import { useAuth } from './context/AuthContext'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function RoleRoute({ role, children }) {
  const { isAuthenticated, user } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return user?.role === role ? children : <Navigate to="/login" replace />
}

export default function App() {
  const { isAuthenticated, user } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <RedirectByRole role={user?.role} /> : <LoginPage />} />
      <Route
        path="/teacher"
        element={
          <RoleRoute role="teacher">
            <TeacherDashboard />
          </RoleRoute>
        }
      />
      <Route
        path="/student"
        element={
          <RoleRoute role="student">
            <StudentDashboard />
          </RoleRoute>
        }
      />
      <Route path="*" element={<RedirectByRole role={user?.role} />} />
    </Routes>
  )
}

function RedirectByRole({ role }) {
  if (role === 'teacher') return <Navigate to="/teacher" replace />
  if (role === 'student') return <Navigate to="/student" replace />
  return <Navigate to="/login" replace />
}
