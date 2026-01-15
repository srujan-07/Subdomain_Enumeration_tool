import React, { useMemo, useState } from 'react'
import { mockPages } from '../data/mock'

type Page = typeof mockPages[number]

type PageListProps = {
  pages?: Page[]
  onSelect?: (page: Page) => void
}

const severityWeight: Record<string, number> = { critical: 4, high: 3, medium: 2, low: 1 }

export const PageList: React.FC<PageListProps> = ({ pages = mockPages, onSelect }) => {
  const [severity, setSeverity] = useState<string>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')

  const filtered = useMemo(() => {
    return pages.filter((p) => {
      const sevMatch =
        severity === 'all' || p.issues.some((i) => severityWeight[i.severity || 'low'] >= severityWeight[severity])
      const typeMatch = typeFilter === 'all' || p.type === typeFilter
      return sevMatch && typeMatch
    })
  }, [pages, severity, typeFilter])

  return (
    <div className="card p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-3 gap-3">
        <h3 className="text-lg font-semibold">Pages</h3>
        <div className="flex gap-2 text-sm">
          <select className="border rounded-lg px-2 py-1" value={severity} onChange={(e) => setSeverity(e.target.value)}>
            <option value="all">Severity: All</option>
            <option value="medium">Medium+</option>
            <option value="high">High+</option>
          </select>
          <select className="border rounded-lg px-2 py-1" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="all">Type: All</option>
            <option value="login">Login</option>
            <option value="dashboard">Dashboard</option>
            <option value="list">List</option>
            <option value="form">Form</option>
            <option value="wizard">Wizard</option>
            <option value="report">Report</option>
          </select>
        </div>
      </div>
      <div className="flex-1 overflow-auto divide-y divide-slate-100">
        {filtered.map((page) => (
          <button
            key={page.url}
            onClick={() => onSelect?.(page)}
            className="w-full text-left py-3 px-2 hover:bg-slate-50"
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="font-semibold text-slate-900 text-sm">{page.url}</div>
                <div className="text-xs text-slate-500 capitalize">{page.type}</div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-slate-900">{page.score}</div>
                <div className="text-xs text-slate-500">Hygiene</div>
              </div>
            </div>
            <div className="flex gap-2 mt-2 flex-wrap">
              {page.issues.slice(0, 3).map((issue, idx) => (
                <span key={idx} className="badge bg-slate-100 text-slate-700">
                  {issue.category}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
