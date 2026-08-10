export default function MetricBox({ icon, label, value, color = '#818cf8', bg = 'rgba(129, 140, 248, 0.15)' }) {
  return (
    <div className="metric-box">
      <div className="metric-icon" style={{ color, background: bg }}>
        <i className={icon} />
      </div>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  )
}
