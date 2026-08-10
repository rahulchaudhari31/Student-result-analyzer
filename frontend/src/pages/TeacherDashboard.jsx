import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { overviewAPI, resultsAPI, studentsAPI, getErrorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'
import Spinner from '../components/ui/Spinner'
import Alert from '../components/ui/Alert'
import MetricBox from '../components/ui/MetricBox'
import SectionTitle from '../components/ui/SectionTitle'
import StudentProfile from '../components/StudentProfile'
import {
  AdvancedInsightsTab,
  DetailedListTab,
  FailuresTab,
  MetricCards,
  OverviewTab,
  SubjectAnalysisTab,
  TopPerformersTab,
} from '../components/AnalysisView'
import { SimpleLineChart } from '../components/charts/Charts'
import { DEPARTMENTS, YEARS } from '../config'

const NAV = [
  { id: 'upload', label: 'Upload', icon: 'fas fa-upload' },
  { id: 'saved', label: 'Saved', icon: 'fas fa-folder-open' },
  { id: 'search', label: 'Search', icon: 'fas fa-search' },
  { id: 'overview', label: 'Overview', icon: 'fas fa-building' },
  { id: 'logout', label: 'Logout', icon: 'fas fa-sign-out-alt' },
]

const ANALYSIS_TABS = [
  { id: 'overview', label: 'Overview', icon: 'fas fa-tachometer-alt' },
  { id: 'top', label: 'Top Performers', icon: 'fas fa-trophy' },
  { id: 'failures', label: 'Failures', icon: 'fas fa-user-times' },
  { id: 'subjects', label: 'Subject Analysis', icon: 'fas fa-book' },
  { id: 'detailed', label: 'Detailed List', icon: 'fas fa-list' },
  { id: 'advanced', label: 'Advanced Insights', icon: 'fas fa-chart-line' },
]

export default function TeacherDashboard() {
  const [tab, setTab] = useState('upload')
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <nav className="navbar">
        <div className="navbar-inner">
          {NAV.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${tab === item.id ? 'active' : ''}`}
              onClick={() => (item.id === 'logout' ? handleLogout() : setTab(item.id))}
            >
              <i className={item.icon} />
              {item.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="content">
        {tab === 'upload' && <UploadTab />}
        {tab === 'saved' && <SavedTab />}
        {tab === 'search' && <SearchTab />}
        {tab === 'overview' && <OverviewTab2 />}
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

function AnalysisTabs({ analysis }) {
  const [active, setActive] = useState('overview')

  return (
    <div>
      <div className="mini-tabs">
        {ANALYSIS_TABS.map((t) => (
          <button
            key={t.id}
            className={`mini-tab ${active === t.id ? 'active' : ''}`}
            onClick={() => setActive(t.id)}
          >
            <i className={t.icon} style={{ marginRight: 6 }} />
            {t.label}
          </button>
        ))}
      </div>
      {active === 'overview' && <OverviewTab analysis={analysis} />}
      {active === 'top' && <TopPerformersTab analysis={analysis} />}
      {active === 'failures' && <FailuresTab analysis={analysis} />}
      {active === 'subjects' && <SubjectAnalysisTab analysis={analysis} />}
      {active === 'detailed' && <DetailedListTab analysis={analysis} />}
      {active === 'advanced' && <AdvancedInsightsTab analysis={analysis} />}
    </div>
  )
}

function UploadTab() {
  const [file, setFile] = useState(null)
  const [examTag, setExamTag] = useState('')
  const [department, setDepartment] = useState(DEPARTMENTS[0])
  const [year, setYear] = useState(YEARS[0])
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)
  const [saveMsg, setSaveMsg] = useState(null)
  const { user } = useAuth()

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a PDF file first.')
      return
    }
    if (!examTag) {
      setError('Please provide an Exam Name to proceed.')
      return
    }
    setError(null)
    setSaveMsg(null)
    setLoading(true)
    try {
      const { data } = await resultsAPI.analyze(file)
      setAnalysis(data)
    } catch (err) {
      setError(getErrorMessage(err, 'No data found. Please check the PDF format.'))
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setSaveMsg(null)
    try {
      const { data } = await resultsAPI.save({
        file_name: file.name,
        exam_tag: examTag,
        department,
        year,
        students_data: analysis.students,
        uploaded_by: user?.name || 'Unknown',
        summary: analysis.summary,
      })
      setSaveMsg(`Success! Data archived securely. (ID: ${data.message})`)
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to save data to cloud.'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <SectionTitle icon="fas fa-upload">Upload Result PDF</SectionTitle>
      <div className="glass-card">
        <div className="grid grid-3 mb-16">
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="field-label">PDF File</label>
            <input
              type="file"
              accept=".pdf"
              className="input input-file"
              onChange={(e) => setFile(e.target.files[0] || null)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="field-label">Exam Name</label>
            <input
              className="input"
              placeholder="e.g., SE Computer May 2024"
              value={examTag}
              onChange={(e) => setExamTag(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="field-label">Department</label>
            <select className="select" value={department} onChange={(e) => setDepartment(e.target.value)}>
              {DEPARTMENTS.map((d) => (
                <option key={d}>{d}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-2 mb-16">
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="field-label">Year</label>
            <select className="select" value={year} onChange={(e) => setYear(e.target.value)}>
              {YEARS.map((y) => (
                <option key={y}>{y}</option>
              ))}
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0, display: 'flex', alignItems: 'flex-end' }}>
            <button className="btn btn-primary btn-block" onClick={handleAnalyze} disabled={loading}>
              {loading ? <Spinner label="Processing…" /> : <><i className="fas fa-cogs" /> Analyze PDF</>}
            </button>
          </div>
        </div>
      </div>

      {error && <Alert type="error">{error}</Alert>}
      {saveMsg && <Alert type="success">{saveMsg}</Alert>}

      {analysis && (
        <div className="mt-16">
          <Alert type="success">
            Successfully processed {analysis.students.length} student records (detected {analysis.pdf_type.toUpperCase()} format)
          </Alert>
          <div className="mb-16">
            <MetricCards summary={analysis.summary} />
          </div>
          <AnalysisTabs analysis={analysis} />
          <div className="glass-card" style={{ textAlign: 'center' }}>
            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
              <i className="fas fa-cloud-upload-alt" />
              {saving ? 'Saving…' : 'Save Data to Cloud'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function SavedTab() {
  const [files, setFiles] = useState(null)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [deptFilter, setDeptFilter] = useState('All')
  const [yearFilter, setYearFilter] = useState('All')
  const [activeFile, setActiveFile] = useState(null)

  const load = useCallback(async () => {
    setError(null)
    try {
      const { data } = await resultsAPI.list()
      setFiles(data)
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load saved results.'))
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  if (activeFile) {
    return (
      <div>
        <button className="btn btn-ghost btn-sm mb-16" onClick={() => setActiveFile(null)}>
          <i className="fas fa-arrow-left" /> Back to List
        </button>
        <SectionTitle icon="fas fa-chart-bar">
          Analysis: {activeFile.exam_tag || 'Unknown'}
        </SectionTitle>
        <MetricCards summary={activeFile.summary || {}} />
        <AnalysisTabs
          analysis={{
            students: activeFile.students_data || [],
            summary: activeFile.summary || {},
            top_students: [],
            failed_students: [],
            subject_grade_summary: [],
            grade_distribution: {},
            batch_statistics: {},
            pdf_type: 'saved',
          }}
        />
      </div>
    )
  }

  if (error) return <Alert type="error">{error}</Alert>
  if (!files) return <Spinner label="Loading archived results…" />

  const filtered = files.filter((f) => {
    const q = search.toLowerCase().trim()
    const tag = String(f.exam_tag || '').toLowerCase()
    const fname = String(f.file_name || '').toLowerCase()
    if (q && !tag.includes(q) && !fname.includes(q)) return false
    if (deptFilter !== 'All' && f.department !== deptFilter) return false
    if (yearFilter !== 'All' && f.year !== yearFilter) return false
    return true
  })

  return (
    <div>
      <SectionTitle icon="fas fa-folder-open">Archived Results</SectionTitle>

      <div className="glass-card" style={{ padding: 16 }}>
        <div className="grid grid-3">
          <div className="form-group">
            <label className="field-label">Search Results</label>
            <input
              className="input"
              placeholder="Search by Exam Name…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="field-label">Department</label>
            <select className="select" value={deptFilter} onChange={(e) => setDeptFilter(e.target.value)}>
              <option>All</option>
              {DEPARTMENTS.map((d) => (
                <option key={d}>{d}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="field-label">Year</label>
            <select className="select" value={yearFilter} onChange={(e) => setYearFilter(e.target.value)}>
              <option>All</option>
              {YEARS.map((y) => (
                <option key={y}>{y}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {filtered.length === 0 ? (
        <Alert type="info">No results match your filters.</Alert>
      ) : (
        <div className="grid grid-2 mt-16">
          {filtered.map((f) => (
            <div key={f.id} className="saved-card">
              <div className="saved-card-header">
                <h4 title={f.exam_tag}>{f.exam_tag || 'N/A'}</h4>
                <span
                  style={{
                    fontSize: '0.75rem',
                    color: '#94a3b8',
                    background: 'rgba(255,255,255,0.1)',
                    padding: '4px 8px',
                    borderRadius: 12,
                    whiteSpace: 'nowrap',
                  }}
                >
                  {formatDate(f.uploaded_at)}
                </span>
              </div>
              <div className="saved-meta">
                <i className="fas fa-building" style={{ color: '#818cf8', marginRight: 6 }} />
                {f.department || 'N/A'} &nbsp;|&nbsp;
                <i className="fas fa-calendar" style={{ color: '#818cf8', marginRight: 6 }} />
                {f.year || 'N/A'}
              </div>
              <div className="saved-stats">
                <div className="saved-stat">
                  <div className="label">Students</div>
                  <div className="value">{f.total_students ?? 0}</div>
                </div>
                <div className="saved-stat">
                  <div className="label">Pass Rate</div>
                  <div className="value" style={{ color: '#4ade80' }}>
                    {f.summary?.pass_percentage ?? 0}%
                  </div>
                </div>
                <div className="saved-stat">
                  <div className="label">Avg SGPA</div>
                  <div className="value" style={{ color: '#fbbf24' }}>
                    {f.summary?.average_sgpa ?? 0}
                  </div>
                </div>
              </div>
              <button
                className="btn btn-primary btn-block mt-16"
                onClick={() => setActiveFile(f)}
              >
                <i className="fas fa-chart-bar" /> View Dashboard
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function SearchTab() {
  const [options, setOptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [student, setStudent] = useState(null)

  useEffect(() => {
    studentsAPI
      .identifiers()
      .then(({ data }) => setOptions(Object.entries(data).map(([prn, name]) => `${name} | ${prn}`)))
      .catch((err) => setError(getErrorMessage(err, 'Failed to load student list.')))
      .finally(() => setLoading(false))
  }, [])

  const selected = query ? options.find((o) => o === query) : null

  const loadStudent = async (prn) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await studentsAPI.history(prn)
      setStudent(data)
    } catch (err) {
      setError(getErrorMessage(err, 'Profile not found.'))
    } finally {
      setLoading(false)
    }
  }

  if (loading && !student) return <Spinner label="Loading student directory…" />

  return (
    <div>
      <SectionTitle icon="fas fa-search">Global Student Search</SectionTitle>
      {error && <Alert type="error">{error}</Alert>}
      <div className="glass-card">
        <label className="field-label">Search Student by Name or PRN</label>
        <select
          className="select"
          value={selected || ''}
          onChange={(e) => {
            const val = e.target.value
            setQuery(val)
            if (val) loadStudent(val.split(' | ').pop())
          }}
        >
          <option value="">Search…</option>
          {options.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      </div>
      {student && <StudentProfile student={student} onBack={() => setStudent(null)} />}
    </div>
  )
}

function OverviewTab2() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    overviewAPI
      .get()
      .then(({ data }) => setData(data))
      .catch((err) => setError(getErrorMessage(err, 'Failed to load overview.')))
  }, [])

  if (error) return <Alert type="error">{error}</Alert>
  if (!data) return <Spinner label="Aggregating institutional data…" />

  return (
    <div>
      <SectionTitle icon="fas fa-building">Institutional Performance Overview</SectionTitle>

      <div className="grid grid-4 mb-24">
        <MetricBox icon="fas fa-university" label="Total Students" value={data.total_students} />
        <MetricBox
          icon="fas fa-graduation-cap"
          label="Overall Pass Rate"
          value={`${data.overall_pass_rate}%`}
          color="#4ade80"
          bg="rgba(74, 222, 128, 0.15)"
        />
        <MetricBox
          icon="fas fa-star"
          label="Institutional Avg SGPA"
          value={data.overall_avg_sgpa}
          color="#fbbf24"
          bg="rgba(251, 191, 36, 0.15)"
        />
        <MetricBox
          icon="fas fa-file-alt"
          label="Exams Analyzed"
          value={data.exams_analyzed}
          color="#818cf8"
        />
      </div>

      <h4 className="mb-16">
        <i className="fas fa-building" style={{ marginRight: 8, color: '#818cf8' }} />
        Department-wise Performance
      </h4>
      <div className="grid grid-2 mb-24">
        <SimpleLineChart
          data={data.department_stats}
          xKey="department"
          yKey="pass_rate"
          title="Pass Percentage by Dept"
          color="#818cf8"
        />
        <SimpleLineChart
          data={data.department_stats}
          xKey="department"
          yKey="avg_sgpa"
          title="Average SGPA by Dept"
          color="#fbbf24"
        />
      </div>

      <h4 className="mb-16">
        <i className="fas fa-calendar" style={{ marginRight: 8, color: '#818cf8' }} />
        Year-wise Progression
      </h4>
      <div className="grid grid-2">
        <SimpleLineChart
          data={data.year_stats}
          xKey="year"
          yKey="pass_rate"
          title="Pass Rate Trend across Years"
          color="#a855f7"
        />
      </div>
    </div>
  )
}

function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value).slice(0, 10)
  return d.toISOString().slice(0, 10)
}
