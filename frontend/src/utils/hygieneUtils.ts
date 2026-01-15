import { PageHygieneData } from '../types/hygiene'

/**
 * Business logic utilities for hygiene data processing
 * Pure functions with no side effects - easy to test
 */

/**
 * Sort pages by hygiene score in ascending order
 */
export function sortPagesByScore(
  pages: PageHygieneData[], 
  order: 'asc' | 'desc' = 'asc'
): PageHygieneData[] {
  return [...pages].sort((a, b) => 
    order === 'asc' ? a.score - b.score : b.score - a.score
  )
}

/**
 * Get the N worst performing pages
 */
export function getWorstPages(pages: PageHygieneData[], count: number = 5): PageHygieneData[] {
  return sortPagesByScore(pages, 'asc').slice(0, count)
}

/**
 * Get the N best performing pages
 */
export function getBestPages(pages: PageHygieneData[], count: number = 5): PageHygieneData[] {
  return sortPagesByScore(pages, 'desc').slice(0, count)
}

/**
 * Calculate average hygiene score across all pages
 */
export function calculateAverageScore(pages: PageHygieneData[]): number {
  if (pages.length === 0) return 0
  const sum = pages.reduce((acc, page) => acc + page.score, 0)
  return Math.round(sum / pages.length)
}

/**
 * Calculate total critical issues across all pages
 */
export function calculateTotalCriticalIssues(pages: PageHygieneData[]): number {
  return pages.reduce((acc, page) => acc + page.criticalIssueCount, 0)
}

/**
 * Calculate total issues across all pages
 */
export function calculateTotalIssues(pages: PageHygieneData[]): number {
  return pages.reduce((acc, page) => acc + page.totalIssueCount, 0)
}

/**
 * Group pages by type
 */
export function groupPagesByType(pages: PageHygieneData[]): Record<string, PageHygieneData[]> {
  return pages.reduce((acc, page) => {
    const type = page.type
    if (!acc[type]) acc[type] = []
    acc[type].push(page)
    return acc
  }, {} as Record<string, PageHygieneData[]>)
}

/**
 * Filter pages by score threshold
 */
export function filterPagesByScoreThreshold(
  pages: PageHygieneData[], 
  threshold: number,
  operator: 'below' | 'above' = 'below'
): PageHygieneData[] {
  return pages.filter(page => 
    operator === 'below' ? page.score < threshold : page.score >= threshold
  )
}

/**
 * Calculate hygiene statistics summary
 */
export interface HygieneStats {
  totalPages: number
  averageScore: number
  totalCriticalIssues: number
  totalIssues: number
  worstScore: number
  bestScore: number
  pagesByType: Record<string, number>
}

export function calculateHygieneStats(pages: PageHygieneData[]): HygieneStats {
  if (pages.length === 0) {
    return {
      totalPages: 0,
      averageScore: 0,
      totalCriticalIssues: 0,
      totalIssues: 0,
      worstScore: 0,
      bestScore: 0,
      pagesByType: {},
    }
  }

  const scores = pages.map(p => p.score)
  const grouped = groupPagesByType(pages)
  const pagesByType = Object.entries(grouped).reduce((acc, [type, typePages]) => {
    acc[type] = typePages.length
    return acc
  }, {} as Record<string, number>)

  return {
    totalPages: pages.length,
    averageScore: calculateAverageScore(pages),
    totalCriticalIssues: calculateTotalCriticalIssues(pages),
    totalIssues: calculateTotalIssues(pages),
    worstScore: Math.min(...scores),
    bestScore: Math.max(...scores),
    pagesByType,
  }
}

/**
 * Format URL for display (truncate if too long)
 */
export function formatUrl(url: string, maxLength: number = 50): string {
  if (url.length <= maxLength) return url
  return url.substring(0, maxLength - 3) + '...'
}

/**
 * Search pages by URL or type
 */
export function searchPages(pages: PageHygieneData[], query: string): PageHygieneData[] {
  const lowerQuery = query.toLowerCase()
  return pages.filter(page => 
    page.url.toLowerCase().includes(lowerQuery) || 
    page.type.toLowerCase().includes(lowerQuery)
  )
}
