import { useState, useEffect } from 'react'
import { HygieneDataState } from '../types/hygiene'
import { hygieneService, DataSourceType } from '../services/hygieneService'

/**
 * Configuration options for useHygieneData hook
 */
interface UseHygieneDataOptions {
  sourceType?: DataSourceType
  pollingEnabled?: boolean
  autoFetch?: boolean
}

/**
 * Custom hook to fetch and manage hygiene data
 * 
 * Refactored to use HygieneDataService for better separation of concerns:
 * - Service layer handles all data fetching logic
 * - Hook focuses on React state management and side effects
 * - Easy to switch between mock, REST, and WebSocket
 * 
 * Usage:
 * ```tsx
 * const { pages, loading, error, refetch } = useHygieneData()
 * ```
 * 
 * Advanced usage with options:
 * ```tsx
 * const { pages, loading, error } = useHygieneData({
 *   sourceType: 'rest',
 *   pollingEnabled: true
 * })
 * ```
 */
export function useHygieneData(options: UseHygieneDataOptions = {}): HygieneDataState & {
  refetch: () => Promise<void>
} {
  const {
    sourceType = 'rest',
    pollingEnabled = false,
    autoFetch = true,
  } = options

  const [state, setState] = useState<HygieneDataState>({
    pages: [],
    loading: autoFetch,
    error: null,
    lastUpdated: null,
  })

  // Update service configuration
  useEffect(() => {
    hygieneService.updateConfig({ sourceType })
  }, [sourceType])

  // Fetch data function
  const fetchData = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }))
      
      const pages = await hygieneService.fetchData()
      
      setState({
        pages,
        loading: false,
        error: null,
        lastUpdated: new Date(),
      })
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch hygiene data',
      }))
    }
  }

  // Initial fetch
  useEffect(() => {
    if (!autoFetch) return

    if (sourceType === 'websocket') {
      // WebSocket subscription
      const unsubscribe = hygieneService.subscribeToUpdates(
        (pages) => setState({
          pages,
          loading: false,
          error: null,
          lastUpdated: new Date(),
        }),
        (error) => setState(prev => ({
          ...prev,
          loading: false,
          error: error.message,
        }))
      )
      return unsubscribe
    } else if (pollingEnabled) {
      // REST polling
      const stopPolling = hygieneService.startPolling(
        (pages) => setState({
          pages,
          loading: false,
          error: null,
          lastUpdated: new Date(),
        }),
        (error) => setState(prev => ({
          ...prev,
          loading: false,
          error: error.message,
        }))
      )
      return stopPolling
    } else {
      // One-time fetch
      fetchData()
    }
  }, [sourceType, pollingEnabled, autoFetch])

  return {
    ...state,
    refetch: fetchData,
  }
}
