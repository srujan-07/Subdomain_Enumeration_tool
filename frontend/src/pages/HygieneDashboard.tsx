import React from 'react'
import { HygieneCharts } from '../components/HygieneCharts'
import { LoadingSpinner, ErrorMessage, SectionHeader } from '../components/common'
import { WorstPagesTable, HygieneStatsGrid } from '../components/hygiene'
import { useHygieneData } from '../hooks/useHygieneData'
import { getWorstPages, calculateHygieneStats } from '../utils/hygieneUtils'

/**
 * Hygiene Dashboard page
 * 
 * Refactored for better separation of concerns:
 * - Business logic extracted to utils/hygieneUtils
 * - UI components extracted to components/hygiene
 * - Data fetching delegated to service layer via hook
 * - Component focuses purely on composition and layout
 */
export const HygieneDashboard: React.FC = () => {
  const { pages, loading, error, refetch } = useHygieneData()

  // Calculate derived data using pure utility functions
  const worstPages = getWorstPages(pages, 5)
  const stats = calculateHygieneStats(pages)

  // Loading state
  if (loading) {
    return <LoadingSpinner message="Loading hygiene data..." />
  }

  // Error state
  if (error) {
    return (
      <ErrorMessage 
        title="Error loading hygiene data"
        message={error}
        onRetry={refetch}
      />
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <SectionHeader 
        title="Hygiene Dashboard"
        subtitle="Monitor code quality and identify problematic pages"
      />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Charts Section */}
        <div className="xl:col-span-2">
          <HygieneCharts />
        </div>

        {/* Worst Pages Section */}
        <div className="card p-4">
          <h3 className="text-lg font-semibold mb-4 text-slate-900">
            Worst Performing Pages
          </h3>
          <WorstPagesTable pages={worstPages} maxItems={5} />
        </div>
      </div>

      {/* Summary Statistics */}
      <HygieneStatsGrid stats={stats} />
    </div>
  )
}
