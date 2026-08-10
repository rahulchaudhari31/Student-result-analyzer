import { useState } from 'react'
import MetricBox from './ui/MetricBox'
import SectionTitle from './ui/SectionTitle'
import DataTable from './ui/DataTable'
import Alert from './ui/Alert'
import {
  GradeHeatmap,
  GradePie,
  PassFailDonut,
  SgpaHistogram,
  StackedGradeBar,
} from './charts/Charts'
import { GRADES } from '../config'

const STATUS_COLUMNS = [
  { key: 'Seat No', header: 'Seat No' },
  { key: 'PRN', header: 'PRN' },
  { key: 'Name', header: 'Name' },
  { key: 'SGPA', header: 'SGPA', render: (v) => v ?? 'N/A' },
  { key: 'Result Status', header: 'Result', render: (v) => <ResultBadge value={v} /> },
]

export function ResultBadge({ value }) {
  const pass = value === 'Pass'
  return <span className={`badge ${pass ? 'badge-pass' : 'badge-fail'}`}>{value}</span>
}

export function GradeBadge({ grade }) {
  const fail = ['F', 'FF', 'AB', 'ABS', 'IC'].includes(grade)
  return <span className={`badge ${fail ? 'badge-fail' : 'badge-pass'}`}>{grade}</span>
}

export function MetricCards({ summary }) {
  return (
    <div className="grid grid-4 mb-24">
      <MetricBox icon="fas fa-users" label="Total Students" value={summary.total_students} />
      <MetricBox
        icon="fas fa-check-circle"
        label="Passed"
        value={summary.passed_students}
        color="#4ade80"
        bg="rgba(74, 222, 128, 0.15)"
      />
      <MetricBox
        icon="fas fa-times-circle"
        label="Failed"
        value={summary.failed_students}
        color="#f87171"
        bg="rgba(248, 113, 113, 0.15)"
      />
      <MetricBox
        icon="fas fa-chart-bar"
        label="Avg SGPA"
        value={summary.average_sgpa}
        color="#fbbf24"
        bg="rgba(251, 191, 36, 0.15)"
      />
    </div>
  )
}

export function OverviewTab({ analysis }) {
  const { summary } = analysis
  const valid = analysis.students.filter((s) => s.HasValidSGPA)
  const sgpas = valid.map((s) => s.SGPA)

  return (
    <div>
      <SectionTitle icon="fas fa-tachometer-alt">Performance Overview</SectionTitle>
      <MetricCards summary={summary} />
      <div className="grid grid-2">
        {sgpas.length > 0 && <SgpaHistogram values={sgpas} />}
        <PassFailDonut passed={summary.passed_students} failed={summary.failed_students} />
      </div>
    </div>
  )
}

export function TopPerformersTab({ analysis }) {
  const rows = analysis.top_students.map((s, i) => ({
    Rank: i + 1,
    'Seat No': s['Seat No'],
    Name: s.Name,
    SGPA: s.SGPA,
    Credits: s.Credits,
  }))

  return (
    <div>
      <SectionTitle icon="fas fa-trophy">Top Performers</SectionTitle>
      <DataTable
        columns={[
          { key: 'Rank', header: 'Rank' },
          { key: 'Seat No', header: 'Seat No' },
          { key: 'Name', header: 'Name' },
          { key: 'SGPA', header: 'SGPA' },
          { key: 'Credits', header: 'Credits' },
        ]}
        rows={rows.slice(0, 10)}
      />
    </div>
  )
}

export function FailuresTab({ analysis }) {
  const rows = analysis.failed_students.map((s) => {
    const failedSubs = (s.Subjects || [])
      .filter((sub) => ['F', 'FF', 'AB', 'IC', 'ABS'].includes(sub.Grade))
      .map((sub) => sub['Course Name'])
      .join(', ')
    return {
      'Seat No': s['Seat No'],
      Name: s.Name,
      'SGPA Raw': s.SGPA_Raw,
      'Failed Subjects': failedSubs || 'N/A',
      _row: s,
    }
  })

  if (rows.length === 0) {
    return <Alert type="success">🎉 All students passed!</Alert>
  }

  return (
    <div>
      <SectionTitle icon="fas fa-user-times">Failure Analysis</SectionTitle>
      <DataTable
        columns={[
          { key: 'Seat No', header: 'Seat No' },
          { key: 'Name', header: 'Name' },
          { key: 'SGPA Raw', header: 'SGPA' },
          { key: 'Failed Subjects', header: 'Failed Subjects' },
        ]}
        rows={rows}
      />
    </div>
  )
}

export function SubjectAnalysisTab({ analysis }) {
  const [studentFilter, setStudentFilter] = useState('All Students')
  const [selectedSubject, setSelectedSubject] = useState(null)

  let subjectRows = [...(analysis.subject_grade_summary || [])].sort(
    (a, b) => b['Failure Rate (%)'] - a['Failure Rate (%)'],
  )

  const studentNames = ['All Students', ...new Set(analysis.students.map((s) => s.Name))]
  if (studentFilter !== 'All Students') {
    const student = analysis.students.find((s) => s.Name === studentFilter)
    const subjNames = (student?.Subjects || []).map((sub) => sub['Course Name'])
    subjectRows = subjectRows.filter((r) => subjNames.includes(r['Course Name']))
  }

  const subjectNames = [...new Set(subjectRows.map((r) => r['Course Name']))].sort()
  const activeSubject = selectedSubject || subjectNames[0]

  const subjectStats = activeSubject ? subjectRows.find((r) => r['Course Name'] === activeSubject) : null

  const subjectStudents = analysis.students
    .flatMap((s) =>
      (s.Subjects || [])
        .filter((sub) => sub['Course Name'] === activeSubject)
        .map((sub) => ({
          'Seat No': s['Seat No'],
          Name: s.Name,
          Grade: sub.Grade,
          PRN: s.PRN,
          SGPA: s.SGPA || 0,
          isFail: ['F', 'FF', 'AB', 'IC', 'ABS'].includes(sub.Grade),
        })),
    )
    .sort((a, b) => {
      const prio = { O: 0, 'A+': 1, A: 2, 'B+': 3, B: 4, C: 5, P: 6, F: 7, FF: 8, AB: 9, ABS: 10 }
      const pa = prio[a.Grade] ?? 100
      const pb = prio[b.Grade] ?? 100
      return pa - pb || b.SGPA - a.SGPA
    })

  const topSubjectStudents = subjectStudents.slice(0, 10)
  const failedSubjectStudents = subjectStudents.filter((s) => s.isFail)

  return (
    <div>
      <SectionTitle icon="fas fa-book">Subject-wise Grade Distribution</SectionTitle>

      <div className="grid grid-2 mb-16" style={{ gridTemplateColumns: '1fr 1fr', maxWidth: 700 }}>
        <div className="form-group">
          <label className="field-label">Filter by Student</label>
          <select className="select" value={studentFilter} onChange={(e) => setStudentFilter(e.target.value)}>
            {studentNames.map((n) => (
              <option key={n}>{n}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label className="field-label">Select Subject</label>
          <select className="select" value={activeSubject || ''} onChange={(e) => setSelectedSubject(e.target.value)}>
            {subjectNames.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>
      </div>

      <h5 style={{ marginBottom: 12 }}>
        <i className="fas fa-sort-amount-down" style={{ marginRight: 8, color: '#818cf8' }} />
        Critical Subjects (Highest Failure Rates)
      </h5>
      <DataTable
        columns={[
          { key: 'Course Name', header: 'Course Name' },
          { key: 'Total Students', header: 'Total' },
          ...GRADES.map((g) => ({ key: g, header: g, sortable: false })),
          { key: 'Failure Rate (%)', header: 'Failure %' },
        ]}
        rows={subjectRows.slice(0, 10)}
      />

      <div className="mt-16 mb-16">
        <StackedGradeBar data={subjectRows.slice(0, 15)} grades={GRADES} />
      </div>

      <SectionTitle icon="fas fa-microscope">Individual Subject Analysis</SectionTitle>
      {subjectStats && (
        <>
          <div className="grid grid-4 mb-24">
            <MetricBox icon="fas fa-users" label="Total Students" value={subjectStats['Total Students']} />
            <MetricBox
              icon="fas fa-percentage"
              label="Pass Rate"
              value={`${subjectStats['Total Students'] > 0 ? ((1 - subjectStats.F / subjectStats['Total Students']) * 100).toFixed(1) : 0}%`}
              color="#4ade80"
              bg="rgba(74, 222, 128, 0.15)"
            />
            <MetricBox
              icon="fas fa-times-circle"
              label="Failures"
              value={subjectStats.F}
              color="#f87171"
              bg="rgba(248, 113, 113, 0.15)"
            />
            <MetricBox
              icon="fas fa-crown"
              label="Top Grade"
              value={GRADES.find((g) => subjectStats[g] > 0) || 'N/A'}
              color="#fbbf24"
              bg="rgba(251, 191, 36, 0.15)"
            />
          </div>

          <div className="grid grid-2 mb-16">
            <GradePie
              data={GRADES.filter((g) => subjectStats[g] > 0).map((g) => ({ name: g, value: subjectStats[g] }))}
              title={`Grade Distribution - ${activeSubject}`}
            />
            <div>
              <h5 style={{ marginBottom: 12 }}>
                <i className="fas fa-trophy" style={{ marginRight: 8, color: '#818cf8' }} />
                Top Performers in {activeSubject}
              </h5>
              <DataTable
                columns={[
                  { key: 'Seat No', header: 'Seat No' },
                  { key: 'Name', header: 'Name' },
                  { key: 'Grade', header: 'Grade', render: (v) => <GradeBadge grade={v} /> },
                  { key: 'SGPA', header: 'SGPA' },
                ]}
                rows={topSubjectStudents}
              />
            </div>
          </div>

          <h5 style={{ marginBottom: 12 }}>❌ Students who failed in {activeSubject}</h5>
          {failedSubjectStudents.length > 0 ? (
            <DataTable
              columns={[
                { key: 'Seat No', header: 'Seat No' },
                { key: 'Name', header: 'Name' },
                { key: 'Grade', header: 'Grade', render: (v) => <GradeBadge grade={v} /> },
                { key: 'PRN', header: 'PRN' },
              ]}
              rows={failedSubjectStudents}
            />
          ) : (
            <Alert type="success">No students failed in {activeSubject}! 🎉</Alert>
          )}
        </>
      )}
    </div>
  )
}

export function DetailedListTab({ analysis }) {
  const [minSgpa, setMinSgpa] = useState(0)
  const [status, setStatus] = useState('All')
  const [sort, setSort] = useState('High to Low')

  let rows = analysis.students
    .filter((s) => !s.Subjects)
    .map((s) => ({ ...s }))
  rows = analysis.students.map(({ Subjects, ...rest }) => rest)

  rows = rows.filter((r) => r.SGPA >= minSgpa)
  if (status !== 'All') rows = rows.filter((r) => r['Result Status'] === status)
  rows = [...rows].sort((a, b) => (sort === 'High to Low' ? b.SGPA - a.SGPA : a.SGPA - b.SGPA))

  return (
    <div>
      <SectionTitle icon="fas fa-list">Complete Student Registry</SectionTitle>
      <div className="grid grid-3 mb-16">
        <div className="form-group">
          <label className="field-label">Min SGPA: {minSgpa}</label>
          <input
            type="range"
            min="0"
            max="10"
            step="0.1"
            value={minSgpa}
            onChange={(e) => setMinSgpa(parseFloat(e.target.value))}
            style={{ width: '100%' }}
          />
        </div>
        <div className="form-group">
          <label className="field-label">Status</label>
          <select className="select" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option>All</option>
            <option>Pass</option>
            <option>Fail</option>
          </select>
        </div>
        <div className="form-group">
          <label className="field-label">Sort</label>
          <select className="select" value={sort} onChange={(e) => setSort(e.target.value)}>
            <option>High to Low</option>
            <option>Low to High</option>
          </select>
        </div>
      </div>
      <DataTable
        columns={[
          { key: 'Seat No', header: 'Seat No' },
          { key: 'PRN', header: 'PRN' },
          { key: 'Name', header: 'Name' },
          { key: 'SGPA', header: 'SGPA' },
          { key: 'Result Status', header: 'Result', render: (v) => <ResultBadge value={v} /> },
          { key: 'Passed Subjects', header: 'Passed' },
          { key: 'Total Subjects', header: 'Total' },
          { key: 'Credits', header: 'Credits' },
        ]}
        rows={rows}
      />
    </div>
  )
}

export function AdvancedInsightsTab({ analysis }) {
  const valid = analysis.students.filter((s) => s.HasValidSGPA)
  const sgpas = valid.map((s) => s.SGPA)
  const stats = analysis.batch_statistics?.sgpa_stats

  return (
    <div>
      <SectionTitle icon="fas fa-chart-line">Advanced Statistical Analysis</SectionTitle>

      {stats && sgpas.length > 0 && (
        <div className="grid grid-2 mb-16">
          <div className="glass-card">
            <h5 style={{ marginBottom: 16 }}>SGPA Distribution Statistics</h5>
            <StatRow label="Mean SGPA" value={stats.mean.toFixed(2)} />
            <StatRow label="Median SGPA" value={stats.median.toFixed(2)} />
            <StatRow label="Standard Deviation" value={stats.std.toFixed(2)} />
            <StatRow label="Range" value={`${stats.min} – ${stats.max}`} />
            <StatRow label="Top 10% Cutoff" value={`> ${stats.p90.toFixed(2)}`} />
            <StatRow label="Bottom 10% Cutoff" value={`< ${stats.p10.toFixed(2)}`} />
          </div>
          <SgpaHistogram values={sgpas} title="SGPA Distribution" />
        </div>
      )}

      <GradeHeatmap data={analysis.subject_grade_summary} />

      <div className="mt-16">
        <GradePie
          data={Object.entries(analysis.grade_distribution || {}).map(([name, value]) => ({ name, value }))}
          title="Overall Grade Distribution"
        />
      </div>
    </div>
  )
}

function StatRow({ label, value }) {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        padding: '8px 0',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
      }}
    >
      <span>{label}</span>
      <strong style={{ color: '#f8fafc' }}>{value}</strong>
    </div>
  )
}
