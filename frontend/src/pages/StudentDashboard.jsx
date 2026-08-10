import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { studentsAPI, getErrorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'
import Spinner from '../components/ui/Spinner'
import Alert from '../components/ui/Alert'
import SectionTitle from '../components/ui/SectionTitle'
import StudentProfile from '../components/StudentProfile'

export default function StudentDashboard() {
  const [options, setOptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [student, setStudent] = useState(null)
  const [loadingProfile, setLoadingProfile] = useState(false)

  const { logout, user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    studentsAPI
      .identifiers()
      .then(({ data }) => setOptions(Object.entries(data).map(([prn, name]) => `${name} | ${prn}`)))
      .catch((err) => setError(getErrorMessage(err, 'Failed to load student directory.')))
      .finally(() => setLoading(false))
  }, [])

  const loadStudent = async (prn) => {
    setLoadingProfile(true)
    setError(null)
    try {
      const { data } = await studentsAPI.history(prn)
      setStudent(data)
    } catch (err) {
      setError(getErrorMessage(err, 'Profile data not found.'))
    } finally {
      setLoadingProfile(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <nav className="navbar">
        <div className="navbar-inner">
          <button className="nav-item active">
            <i className="fas fa-user-graduate" /> My Dashboard
          </button>
          <button className="nav-item" onClick={handleLogout}>
            <i className="fas fa-sign-out-alt" /> Logout
          </button>
        </div>
      </nav>

      <main className="content">
        {user && (
          <div style={{ textAlign: 'center', marginBottom: 20 }}>
            <span className="muted">
              Signed in as <strong style={{ color: '#f8fafc' }}>{user.name}</strong>
            </span>
          </div>
        )}

        <SectionTitle icon="fas fa-search">Find Your Records</SectionTitle>

        {error && <Alert type="error">{error}</Alert>}

        <div className="glass-card">
          <label className="field-label">Confirm Identity</label>
          {loading ? (
            <Spinner label="Loading directory…" />
          ) : (
            <select
              className="select"
              value={query}
              onChange={(e) => {
                const val = e.target.value
                setQuery(val)
                if (val) loadStudent(val.split(' | ').pop())
              }}
            >
              <option value="">Select Your Profile…</option>
              {options.map((o) => (
                <option key={o} value={o}>
                  {o}
                </option>
              ))}
            </select>
          )}
        </div>

        {loadingProfile && <Spinner label="Retrieving academic records…" />}

        {student && !loadingProfile && <StudentProfile student={student} />}
      </main>

      <footer className="footer">
        <p>
          Developed by <span style={{ color: '#818cf8', fontWeight: 600 }}>Sakshi, Rahul, Sakshi</span>
          &nbsp;|&nbsp; Smart Result Analysis System
        </p>
      </footer>
    </div>
  )
}
