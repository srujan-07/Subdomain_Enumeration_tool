/**
 * Hygiene data models for the QA inspection platform
 */

export interface HygieneIssue {
  title: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  category: 'functional' | 'ui' | 'performance' | 'accessibility' | 'content' | 'security'
}

export interface PageHygieneData {
  url: string
  type: string
  score: number
  criticalIssueCount: number
  totalIssueCount: number
  issues: HygieneIssue[]
}

export interface HygieneDataState {
  pages: PageHygieneData[]
  loading: boolean
  error: string | null
  lastUpdated: Date | null
}

export type HygieneScoreLevel = 'excellent' | 'good' | 'warning' | 'critical'

/**
 * Get color class based on hygiene score
 */
export function getScoreColor(score: number): string {
  if (score > 75) return 'text-green-600'
  if (score >= 50) return 'text-yellow-600'
  return 'text-red-600'
}

/**
 * Get background color class based on hygiene score
 */
export function getScoreBgColor(score: number): string {
  if (score > 75) return 'bg-green-100 text-green-800'
  if (score >= 50) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

/**
 * Get hygiene score level
 */
export function getScoreLevel(score: number): HygieneScoreLevel {
  if (score > 75) return 'excellent'
  if (score >= 50) return 'good'
  if (score >= 25) return 'warning'
  return 'critical'
}
