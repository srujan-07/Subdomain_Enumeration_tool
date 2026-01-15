import React from 'react'
import { mockPages } from '../data/mock'

export const ScanHistory: React.FC = () => {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">Scan History (mock)</h3>
        <span className="badge bg-slate-100 text-slate-600">Last 5</span>
      </div>
      <div className="divide-y divide-slate-100 text-sm">
        {mockPages.map((p, idx) => (
          <div key={idx} className="py-3 flex items-center justify-between">
            <div>
              <div className="font-semibold text-slate-900">{p.url}</div>
              <div className="text-xs text-slate-500">Score: {p.score} · Type: {p.type}</div>
            </div>
            <div className="text-xs text-slate-500">2024-01-15 10:{idx}0</div>
          </div>
        ))}
      </div>
    </div>
  )
}
