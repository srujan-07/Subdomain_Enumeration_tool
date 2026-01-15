import React from 'react'
import { mockActivity } from '../data/mock'

type ActivityFeedProps = {
  items?: typeof mockActivity
}

const levelClass: Record<string, string> = {
  info: 'text-slate-700',
  success: 'text-success',
  warning: 'text-warning',
  error: 'text-danger',
}

export const ActivityFeed: React.FC<ActivityFeedProps> = ({ items = mockActivity }) => {
  return (
    <div className="card p-4 h-full">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">Activity</h3>
        <span className="badge bg-slate-100 text-slate-600">Live</span>
      </div>
      <div className="space-y-2 text-sm">
        {items.map((item, idx) => (
          <div key={idx} className="flex gap-3">
            <span className="text-slate-400 w-16">{item.ts}</span>
            <span className={`${levelClass[item.level] || 'text-slate-700'}`}>{item.message}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
