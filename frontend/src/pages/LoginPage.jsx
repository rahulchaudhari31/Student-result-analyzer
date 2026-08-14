import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI, getErrorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'
import Alert from '../components/ui/Alert'

export default function LoginPage() {
  const [mode, setMode] = useState('login')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('teacher')

  const [regName, setRegName] = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regPassword, setRegPassword] = useState('')
  const [regRole, setRegRole] = useState('student')

  const { login } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const { data } = await authAPI.login(email, password)
      if (data.role !== role) {
        setError(`Role mismatch. This account is registered as '${data.role}'.`)
        return
      }
      login(data)
      navigate(data.role === 'teacher' ? '/teacher' : '/student')
    } catch (err) {
      setError(getErrorMessage(err, 'Login failed. Check your credentials.'))
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setError(null)
    if (regPassword.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    if (!regName || !regEmail) {
      setError('Please fill all fields.')
      return
    }
    setLoading(true)
    try {
      const { data } = await authAPI.register(regEmail, regPassword, regName, regRole)
      login(data)
      navigate(data.role === 'teacher' ? '/teacher' : '/student')
    } catch (err) {
      setError(getErrorMessage(err, 'Registration failed. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="app-header">
        <h1>Smart Result Analysis System</h1>
        <p>Advanced Analytics &amp; Academic Tracking System</p>
      </div>

      <div className="glass-card auth-card">
        <div className="tabs">
          <button
            className={`tab-btn ${mode === 'login' ? 'active' : ''}`}
            onClick={() => {
              setMode('login')
              setError(null)
            }}
          >
            <i className="fas fa-lock" style={{ marginRight: 8 }} />Login
          </button>
          <button
            className={`tab-btn ${mode === 'register' ? 'active' : ''}`}
            onClick={() => {
              setMode('register')
              setError(null)
            }}
          >
            <i className="fas fa-user-plus" style={{ marginRight: 8 }} />Register
          </button>
        </div>

        {error && <Alert type="error">{error}</Alert>}

        {mode === 'login' ? (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label className="field-label">Email</label>
              <input
                className="input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="field-label">Password</label>
              <input
                className="input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="field-label">Role</label>
              <select className="select" value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="teacher">Teacher</option>
                <option value="student">Student</option>
              </select>
            </div>
            <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label className="field-label">Full Name</label>
              <input
                className="input"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="field-label">Email Address</label>
              <input
                className="input"
                type="email"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="field-label">Create Password</label>
              <input
                className="input"
                type="password"
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="field-label">I am a...</label>
              <select className="select" value={regRole} onChange={(e) => setRegRole(e.target.value)}>
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
              </select>
            </div>
            <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
              {loading ? 'Creating account…' : 'Create Account'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
