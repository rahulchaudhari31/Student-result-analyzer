import { useState } from 'react'
import { GradeBadge } from './AnalysisView'
import { SgpaLineChart } from './charts/Charts'
import DataTable from './ui/DataTable'
import Alert from './ui/Alert'
import { GRADE_POINTS } from '../config'

export default function StudentProfile({ student, onBack }) {
  const [openTranscript, setOpenTranscript] = useState(null)
  const results = student.results || []
  const prediction = student.predicted_next_sgpa
  const failedSubjects = student.failed_subjects || []

  const subjectData = []
  results.forEach((r) => {
    ;(r.Subjects || []).forEach((sub) => {
      subjectData.push({
        'Course Name': sub['Course Name'] || sub['Course Code'] || 'Unknown',
        Grade: (sub.Grade || '').trim(),
        GradePoint: GRADE_POINTS[sub.Grade] ?? 0,
        Exam: r.Exam,
      })
    })
  })

  return (
    <div>
      {onBack && (
        <button className="btn btn-ghost btn-sm mb-16" onClick={onBack}>
          <i className="fas fa-arrow-left" /> Back
        </button>
      )}

      <div className="profile-hero">
        <div className="profile-avatar">
          <i className="fas fa-user-graduate" />
        </div>
        <div className="profile-info">
          <h2>{student.name}</h2>
          <p>
            <i className="fas fa-id-card" style={{ marginRight: 8 }} /> {student.prn}
            {student.mother && (
              <>
                <span style={{ margin: '0 10px' }}>|</span>
                <i className="fas fa-user" style={{ marginRight: 8 }} /> {student.mother}
              </>
            )}
          </p>
        </div>
      </div>

      {(prediction !== null || failedSubjects.length > 0) && (
        <div className="grid grid-2 mb-16">
          {prediction !== null && (
            <div
              className="glass-card"
              style={{ borderLeft: '4px solid #818cf8', marginBottom: 0 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 15 }}>
                <div
                  className="metric-icon"
                  style={{ background: 'rgba(129, 140, 248, 0.2)', color: '#818cf8', marginBottom: 0 }}
                >
                  <i className="fas fa-crystal-ball" />
                </div>
                <div>
                  <div className="metric-label">SGPA Projection</div>
                  <div className="metric-value">{prediction}</div>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: 5 }}>
                    Based on performance trend
                  </div>
                </div>
              </div>
            </div>
          )}

          {failedSubjects.length > 0 && (
            <div
              className="glass-card"
              style={{ borderLeft: '4px solid #f87171', background: 'rgba(248, 113, 113, 0.05)', marginBottom: 0 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <i className="fas fa-exclamation-triangle" style={{ color: '#f87171' }} />
                <h5 style={{ color: '#f87171', margin: 0, fontSize: '1rem' }}>
                  Subject Failure Alerts
                </h5>
              </div>
              {failedSubjects.slice(0, 6).map((item, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: 8,
                    background: 'rgba(255,255,255,0.05)',
                    borderRadius: 6,
                    marginBottom: 6,
                  }}
                >
                  <span style={{ color: '#e2e8f0', fontSize: '0.85rem' }}>{item.Subject}</span>
                  <span style={{ color: '#f87171', fontWeight: 700, fontSize: '0.85rem' }}>
                    {item.Grade}{' '}
                    <span style={{ color: '#64748b', fontWeight: 400, fontSize: '0.7rem' }}>
                      ({String(item.Exam || '').split(' ')[0]})
                    </span>
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {results.length === 0 ? (
        <Alert type="info">No detailed result history available.</Alert>
      ) : (
        <>
          <h3 className="section-title">
            <i className="fas fa-chart-line" style={{ marginRight: 8, color: '#818cf8' }} />
            Academic Progression
          </h3>

          <div className="mb-16">
            <SgpaLineChart
              data={results.map((r) => ({ Exam: r.Exam, SGPA: r.SGPA }))}
              title="SGPA Growth"
            />
          </div>

          {subjectData.length > 0 && (
            <>
              <h4 className="mb-16">
                <i className="fas fa-chart-bar" style={{ marginRight: 8, color: '#818cf8' }} />
                Subject Performance Analysis
              </h4>
              <div className="chart-card mb-16">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Course</th>
                      <th>Grade</th>
                      <th>Grade Point</th>
                      <th>Exam</th>
                    </tr>
                  </thead>
                  <tbody>
                    {subjectData.map((s, i) => (
                      <tr key={i}>
                        <td>{s['Course Name']}</td>
                        <td>
                          <GradeBadge grade={s.Grade} />
                        </td>
                        <td>{s.GradePoint}</td>
                        <td>{s.Exam}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          <h3 className="section-title">
            <i className="fas fa-layer-group" style={{ marginRight: 8, color: '#818cf8' }} />
            Semester Snapshots
          </h3>
          <div className="grid grid-3 mb-16">
            {results.map((r, i) => {
              const pass = r.Result === 'Pass'
              return (
                <div
                  key={i}
                  className="glass-card"
                  style={{ padding: 20, borderLeft: `4px solid ${pass ? '#4ade80' : '#f87171'}` }}
                >
                  <div
                    style={{
                      fontWeight: 700,
                      fontSize: '0.9rem',
                      color: '#e2e8f0',
                      marginBottom: 10,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                    title={r.Exam}
                  >
                    {r.Exam}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                    <div>
                      <div style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                        SGPA
                      </div>
                      <div style={{ fontSize: '1.6rem', fontWeight: 800, color: pass ? '#4ade80' : '#f87171', lineHeight: 1 }}>
                        {r.SGPA}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase' }}>
                        Result
                      </div>
                      <div
                        style={{
                          fontSize: '0.9rem',
                          fontWeight: 600,
                          color: '#f8fafc',
                          background: pass ? 'rgba(74, 222, 128, 0.1)' : 'rgba(248, 113, 113, 0.1)',
                          padding: '2px 8px',
                          borderRadius: 4,
                        }}
                      >
                        {r.Result}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          <h3 className="section-title">
            <i className="fas fa-file-contract" style={{ marginRight: 8, color: '#818cf8' }} />
            Detailed Transcripts
          </h3>
          {results.map((r, i) => (
            <div key={i} className="glass-card" style={{ padding: 16 }}>
              <button
                className="btn btn-ghost btn-sm btn-block"
                onClick={() => setOpenTranscript(openTranscript === i ? null : i)}
              >
                {r.Exam} (SGPA: {r.SGPA})
                <i className={`fas fa-chevron-${openTranscript === i ? 'up' : 'down'}`} />
              </button>
              {openTranscript === i && (
                <div className="mt-16">
                  <p className="muted mb-16" style={{ fontSize: '0.9rem' }}>
                    <strong>Seat No:</strong> <code>{r.Seat}</code>
                    <span style={{ margin: '0 16px' }}>|</span>
                    <strong>Credits:</strong> <code>{r.Credits}</code>
                  </p>
                  <DataTable
                    columns={[
                      { key: 'Course Code', header: 'Code' },
                      { key: 'Course Name', header: 'Name' },
                      { key: 'Grade', header: 'Grade', render: (v) => <GradeBadge grade={v} /> },
                    ]}
                    rows={r.Subjects || []}
                  />
                </div>
              )}
            </div>
          ))}
        </>
      )}
    </div>
  )
}
