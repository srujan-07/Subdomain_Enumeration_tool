import React from 'react'
import { ActivityFeed } from '../components/ActivityFeed'
import { LiveStats } from '../components/LiveStats'

export const ActiveScans: React.FC = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2 space-y-4">
        <LiveStats />
        <div className="card p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold">Live Scan Monitor</h3>
            <span className="badge bg-success/10 text-success">WebSocket Connected</span>
          </div>
          <div className="text-sm text-slate-600">Real-time progress, hygiene score, and discovered pages.</div>
        </div>
      </div>
      <ActivityFeed />
    </div>
  )
}
