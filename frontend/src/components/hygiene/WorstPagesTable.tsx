import React from 'react'
import { useNavigate } from 'react-router-dom'
import { PageHygieneData } from '../../types/hygiene'
import { getScoreBgColor } from '../../types/hygiene'
import { EmptyState } from '../common'

/**
 * Props for WorstPagesTable component
 */
interface WorstPagesTableProps {
  pages: PageHygieneData[]
  maxItems?: number
  onPageClick?: (url: string) => void
}

/**
 * Reusable component to display worst performing pages
 * Extracted for better separation of concerns
 */
export const WorstPagesTable: React.FC<WorstPagesTableProps> = ({ 
  pages, 
  maxItems = 5,
  onPageClick 
}) => {
  const navigate = useNavigate()

  const handlePageClick = (url: string) => {
    if (onPageClick) {
      onPageClick(url)
    } else {
      const encodedUrl = encodeURIComponent(url)
      navigate(`/pages?url=${encodedUrl}`)
    }
  }

  if (pages.length === 0) {
    return <EmptyState message="No pages found" />
  }

  return (
    <div className="space-y-3">
      {pages.slice(0, maxItems).map((page, index) => (
        <div
          key={page.url}
          className="p-3 border border-slate-200 rounded-lg hover:border-slate-400 hover:shadow-sm transition-all cursor-pointer"
          onClick={() => handlePageClick(page.url)}
        >
          {/* Rank Badge */}
          <div className="flex items-start justify-between mb-2">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-900 text-white text-xs font-bold">
              {index + 1}
            </span>
            <span className={`px-2 py-1 rounded-full text-xs font-bold ${getScoreBgColor(page.score)}`}>
              {page.score}
            </span>
          </div>

          {/* URL - Clickable */}
          <div className="text-sm font-semibold text-blue-600 hover:text-blue-800 mb-1 break-all">
            {page.url}
          </div>

          {/* Metadata */}
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500 capitalize">{page.type}</span>
            <div className="flex items-center gap-2">
              {page.criticalIssueCount > 0 && (
                <span className="text-red-600 font-semibold">
                  {page.criticalIssueCount} critical
                </span>
              )}
              <span className="text-slate-500">
                {page.totalIssueCount} issues
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
