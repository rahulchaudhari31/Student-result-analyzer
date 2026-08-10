export default function SectionTitle({ icon, children, style }) {
  return (
    <h3 className="section-title" style={style}>
      {icon && <i className={icon} style={{ marginRight: 8, color: '#818cf8' }} />}
      {children}
    </h3>
  )
}
