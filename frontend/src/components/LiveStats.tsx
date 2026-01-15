import React from 'react'
import { mockStats } from '../data/mock'
import { Gauge, GaugeChart } from './charts/GaugeChart'

type LiveStatsProps = {
  stats?: typeof mockStats
}

export const LiveStats: React.FC<LiveStatsProps> = ({ stats = mockStats }) => {
  return (
    <div className="card p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-slate-500">Pages discovered</div>
          <div className="text-3xl font-bold">{stats.pagesDiscovered}</div>
        </div>
        <div className="text-sm text-slate-500">
          Status: <span className="font-semibold text-success">{stats.inProgress ? 'Running' : 'Idle'}</span>
        </div>
      </div>
      <div>
        <div className="text-sm text-slate-500 mb-2">Live Hygiene Score</div>
        <GaugeChart value={stats.hygieneScore} />
      </div>
    </div>
  )
}
