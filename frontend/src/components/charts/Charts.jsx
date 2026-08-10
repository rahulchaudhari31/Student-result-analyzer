import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { GRADE_COLORS } from '../../config'

const darkTooltip = {
  backgroundColor: '#0f172a',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: 10,
  color: '#f8fafc',
}

export function SgpaHistogram({ values, title }) {
  const min = Math.floor(Math.min(...values))
  const max = Math.ceil(Math.max(...values))
  const binWidth = Math.max(0.5, (max - min) / 12)
  const bins = {}
  values.forEach((v) => {
    const key = (Math.floor(v / binWidth) * binWidth).toFixed(1)
    bins[key] = (bins[key] || 0) + 1
  })
  const data = Object.entries(bins)
    .map(([bin, count]) => ({ bin, count }))
    .sort((a, b) => parseFloat(a.bin) - parseFloat(b.bin))

  return (
    <div className="chart-card">
      <h5 style={{ marginBottom: 12 }}>{title || 'SGPA Distribution'}</h5>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="bin" stroke="#94a3b8" fontSize={11} />
          <YAxis stroke="#94a3b8" fontSize={11} allowDecimals={false} />
          <Tooltip contentStyle={darkTooltip} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
          <Bar dataKey="count" fill="#00d4ff" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function PassFailDonut({ passed, failed }) {
  const data = [
    { name: 'Pass', value: passed, fill: '#00ff9d' },
    { name: 'Fail', value: failed, fill: '#ff4b4b' },
  ].filter((d) => d.value > 0)

  return (
    <div className="chart-card">
      <h5 style={{ marginBottom: 12 }}>Pass / Fail Ratio</h5>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={70} outerRadius={100} paddingAngle={2}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.fill} />
            ))}
          </Pie>
          <Tooltip contentStyle={darkTooltip} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

export function GradePie({ data, hole = 0, title }) {
  const safeData = (data || []).filter((d) => d.value > 0)
  return (
    <div className="chart-card">
      <h5 style={{ marginBottom: 12 }}>{title || 'Grade Distribution'}</h5>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={safeData}
            dataKey="value"
            nameKey="name"
            innerRadius={hole ? 70 : 0}
            outerRadius={100}
            paddingAngle={hole ? 2 : 0}
          >
            {safeData.map((d) => (
              <Cell key={d.name} fill={GRADE_COLORS[d.name] || '#94a3b8'} />
            ))}
          </Pie>
          <Tooltip contentStyle={darkTooltip} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

export function StackedGradeBar({ data, grades }) {
  const bars = (grades || []).filter((g) => data.some((d) => d[g] > 0))
  return (
    <div className="chart-card">
      <h5 style={{ marginBottom: 12 }}>Grade Count by Subject</h5>
      <ResponsiveContainer width="100%" height={340}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="Course Name" stroke="#94a3b8" fontSize={10} interval={0} angle={-25} textAnchor="end" height={70} />
          <YAxis stroke="#94a3b8" fontSize={11} allowDecimals={false} />
          <Tooltip contentStyle={darkTooltip} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
          <Legend />
          {bars.map((g) => (
            <Bar key={g} dataKey={g} stackId="a" fill={GRADE_COLORS[g] || '#94a3b8'} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function SgpaLineChart({ data, title = 'SGPA Growth' }) {
  return (
    <div className="chart-card">
      <h5 style={{ marginBottom: 12 }}>{title}</h5>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="Exam" stroke="#94a3b8" fontSize={11} />
          <YAxis domain={[0, 10]} stroke="#94a3b8" fontSize={11} />
          <Tooltip contentStyle={darkTooltip} />
          <Line type="monotone" dataKey="SGPA" stroke="#00d4ff" strokeWidth={3} dot={{ r: 5, fill: '#00d4ff' }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export function SimpleLineChart({ data, xKey, yKey, title, color = '#a855f7' }) {
  return (
    <div className="chart-card">
      <h5 style={{ marginBottom: 12 }}>{title}</h5>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey={xKey} stroke="#94a3b8" fontSize={11} />
          <YAxis stroke="#94a3b8" fontSize={11} />
          <Tooltip contentStyle={darkTooltip} />
          <Line type="monotone" dataKey={yKey} stroke={color} strokeWidth={3} dot={{ r: 5, fill: color }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export function GradeHeatmap({ data }) {
  const grades = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F']
  const subjects = (data || []).slice(0, 20)
  const maxCount = Math.max(
    1,
    ...subjects.flatMap((s) => grades.map((g) => Number(s[g] || 0))),
  )

  return (
    <div className="chart-card" style={{ overflowX: 'auto' }}>
      <h5 style={{ marginBottom: 12 }}>Grade Concentration Heatmap</h5>
      <table className="data-table" style={{ minWidth: 500 }}>
        <thead>
          <tr>
            <th>Subject</th>
            {grades.map((g) => (
              <th key={g}>{g}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {subjects.map((s) => (
            <tr key={s['Course Code']}>
              <td style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis' }} title={s['Course Name']}>
                {s['Course Name']}
              </td>
              {grades.map((g) => {
                const v = Number(s[g] || 0)
                const alpha = v === 0 ? 0.05 : 0.25 + (v / maxCount) * 0.75
                return (
                  <td
                    key={g}
                    style={{
                      textAlign: 'center',
                      background: `rgba(16, 185, 129, ${alpha})`,
                      color: v === 0 ? '#64748b' : '#fff',
                    }}
                  >
                    {v || ''}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
