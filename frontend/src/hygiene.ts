/**
 * Type exports for the Hygiene Dashboard
 * Re-export commonly used types and utilities
 */

export type {
  HygieneIssue,
  PageHygieneData,
  HygieneDataState,
  HygieneScoreLevel,
} from './types/hygiene'

export {
  getScoreColor,
  getScoreBgColor,
  getScoreLevel,
} from './types/hygiene'

export { useHygieneData } from './hooks/useHygieneData'
