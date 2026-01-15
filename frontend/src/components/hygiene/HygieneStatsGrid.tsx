import React from 'react'
import { StatCard } from '../common'
import { getScoreColor } from '../../types/hygiene'
import { HygieneStats } from '../../utils/hygieneUtils'

/**
 * Props for HygieneStatsGrid component
 */
interface HygieneStatsGridProps {
  stats: HygieneStats
}

/**
 * Reusable component to display hygiene statistics
 * Extracted for better separation of concerns
 */
export const HygieneStatsGrid: React.FC<HygieneStatsGridProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <StatCard 
        label="Total Pages" 
        value={stats.totalPages}
      />
      <StatCard 
        label="Average Score" 
        value={stats.averageScore}
        valueColor={getScoreColor(stats.averageScore)}
      />
      <StatCard 
        label="Critical Issues" 
        value={stats.totalCriticalIssues}
        valueColor="text-red-600"
      />
    </div>
  )
}
