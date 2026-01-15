import React from 'react'
import { mockPages } from '../data/mock'

type Page = typeof mockPages[number]

type PageDetailProps = {
  page?: Page
}

const severityColor: Record<string, string> = {
  critical: 'bg-danger/10 text-danger',
  high: 'bg-danger/10 text-danger',
  medium: 'bg-warning/10 text-warning',
  low: 'bg-slate-100 text-slate-700',
}

export const PageDetail: React.FC<PageDetailProps> = ({ page }) => {
  if (!page) {
    return (
      <div className="card p-6 text-slate-500 h-full flex items-center justify-center">
        Select a page to inspect its issues.
      </div>
    )
  }
  return (
    <div className="card p-4 h-full">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-slate-500">URL</div>
          <div className="text-lg font-semibold text-slate-900">{page.url}</div>
          <div className="text-xs text-slate-500 capitalize">Type: {page.type}</div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-slate-900">{page.score}</div>
          <div className="text-xs text-slate-500">Hygiene score</div>
        </div>
      </div>
      <div className="mt-4">
        <h4 className="text-sm font-semibold text-slate-700 mb-2">Issues</h4>
        <div className="space-y-2 max-h-80 overflow-auto pr-1">
          {page.issues.map((issue, idx) => (
            <div key={idx} className="p-3 border border-slate-200 rounded-lg">
              <div className="flex items-center justify-between gap-2">
                <div className="font-medium text-slate-900 text-sm">{issue.title}</div>
                <span className={`badge ${severityColor[issue.severity] || 'bg-slate-100 text-slate-700'}`}>
                  {issue.severity}
                </span>
              </div>
              <div className="text-xs text-slate-500 capitalize">{issue.category}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
