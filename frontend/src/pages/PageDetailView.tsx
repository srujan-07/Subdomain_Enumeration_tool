import React from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { LoadingSpinner, StatCard, Badge, SectionHeader } from '../components/common'
import { useHygieneData } from '../hooks/useHygieneData'
import { getScoreColor, getScoreBgColor } from '../types/hygiene'

/**
 * Page detail view - displays detailed information about a specific page
 * Accessed via /pages?url=<encoded-url>
 * 
 * Refactored for better separation of concerns:
 * - Reuses common UI components
 * - Simplified state management
 * - Cleaner component structure
 */
export const PageDetailView: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { pages, loading } = useHygieneData()

  const url = searchParams.get('url')
  const page = pages.find(p => p.url === url)

  if (loading) {
    return <LoadingSpinner message="Loading page details..." />
  }

  if (!url || !page) {
    return (
      <div className="card p-6">
        <h2 className="text-xl font-bold mb-4">Page Not Found</h2>
        <p className="text-slate-600 mb-4">The requested page could not be found.</p>
        <button
          onClick={() => navigate('/hygiene')}
          className="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors"
        >
          Back to Hygiene Dashboard
        </button>
      </div>
    )
  }

  const getSeverityVariant = (severity: string) => {
    switch (severity) {
      case 'critical': return 'danger'
      case 'high': return 'warning'
      case 'medium': return 'warning'
      case 'low': return 'info'
      default: return 'default'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/hygiene')}
          className="text-slate-600 hover:text-slate-900 font-medium transition-colors"
        >
          ← Back
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-900 break-all">{page.url}</h1>
          <p className="text-slate-600 capitalize mt-1">{page.type} page</p>
        </div>
        <Badge variant={page.score > 75 ? 'success' : page.score >= 50 ? 'warning' : 'danger'} size="lg">
          Score: {page.score}
        </Badge>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard 
          label="Hygiene Score" 
          value={page.score}
          valueColor={getScoreColor(page.score)}
        />
        <StatCard 
          label="Critical Issues" 
          value={page.criticalIssueCount}
          valueColor="text-red-600"
        />
        <StatCard 
          label="Total Issues" 
          value={page.totalIssueCount}
        />
      </div>

      {/* Issues List */}
      <div className="card p-6">
        <h2 className="text-xl font-bold mb-4">Issues Detected</h2>
        {page.issues.length === 0 ? (
          <p className="text-slate-600 text-center py-8">No issues detected - Great job!</p>
        ) : (
          <div className="space-y-3">
            {page.issues.map((issue, index) => (
              <div
                key={index}
                className="p-4 border border-slate-200 rounded-lg hover:border-slate-400 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-slate-900 flex-1">{issue.title}</h3>
                  <Badge variant={getSeverityVariant(issue.severity)} size="md">
                    {issue.severity}
                  </Badge>
                </div>
                <div className="text-sm text-slate-600 capitalize">
                  Category: <span className="font-medium">{issue.category}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
