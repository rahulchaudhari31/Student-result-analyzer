import { useState } from 'react'

export default function DataTable({ columns, rows, empty = 'No data available' }) {
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState(null)
  const [sortDir, setSortDir] = useState('asc')

  if (!rows || rows.length === 0) {
    return <div className="empty-state">{empty}</div>
  }

  let visible = rows
  if (search) {
    const q = search.toLowerCase()
    visible = visible.filter((row) =>
      columns.some((col) => String(row[col.key] ?? '').toLowerCase().includes(q)),
    )
  }

  if (sortKey) {
    visible = [...visible].sort((a, b) => {
      const av = a[sortKey]
      const bv = b[sortKey]
      const cmp =
        typeof av === 'number' && typeof bv === 'number'
          ? av - bv
          : String(av).localeCompare(String(bv))
      return sortDir === 'asc' ? cmp : -cmp
    })
  }

  const onSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  const renderCell = (row, col) => {
    const value = row[col.key]
    if (col.render) return col.render(value, row)
    return value ?? '—'
  }

  return (
    <div>
      <div style={{ marginBottom: 12, display: 'flex', gap: 10, alignItems: 'center' }}>
        <input
          className="input"
          style={{ maxWidth: 320 }}
          placeholder="Search…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <span className="muted" style={{ fontSize: '0.85rem' }}>
          {visible.length} of {rows.length}
        </span>
      </div>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  style={{ cursor: col.sortable === false ? 'default' : 'pointer' }}
                  onClick={() => col.sortable !== false && onSort(col.key)}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visible.map((row, i) => (
              <tr key={i}>
                {columns.map((col) => (
                  <td key={col.key}>{renderCell(row, col)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
