import { PageHygieneData, HygieneIssue } from '../types/hygiene'

/**
 * Data service layer for hygiene data
 * Abstracts data fetching logic from components
 * Provides a clean interface for switching between mock, REST, and WebSocket
 */

export type DataSourceType = 'mock' | 'rest' | 'websocket'

/**
 * Configuration for data service
 */
export interface HygieneServiceConfig {
  sourceType: DataSourceType
  apiBaseUrl?: string
  wsUrl?: string
  pollingInterval?: number
  mockDelay?: number
}

/**
 * Default configuration
 */
const DEFAULT_CONFIG: HygieneServiceConfig = {
  sourceType: 'rest',
  apiBaseUrl: 'http://localhost:8000/api',
  wsUrl: 'ws://localhost:8000/ws/hygiene',
  pollingInterval: 5000,
  mockDelay: 500,
}

/**
 * Transform raw API data to typed PageHygieneData
 */
function transformApiData(data: any): PageHygieneData {
  return {
    url: data.url,
    type: data.type,
    score: data.score,
    criticalIssueCount: data.issues?.filter((i: any) => i.severity === 'high' || i.severity === 'critical').length || 0,
    totalIssueCount: data.issues?.length || 0,
    issues: data.issues || [],
  }
}

/**
 * Mock data fetcher (simulates network delay)
 */
async function fetchMockData(config: HygieneServiceConfig): Promise<PageHygieneData[]> {
  const { mockPages } = await import('../data/mock')
  
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, config.mockDelay || 500))
  
  return mockPages.map(page => transformApiData(page))
}

/**
 * REST API fetcher
 */
async function fetchRestData(config: HygieneServiceConfig): Promise<PageHygieneData[]> {
  const response = await fetch(`${config.apiBaseUrl}/hygiene`)
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  const data = await response.json()
  return data.map(transformApiData)
}

/**
 * WebSocket connection manager
 */
export class HygieneWebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  constructor(
    private config: HygieneServiceConfig,
    private onData: (data: PageHygieneData[]) => void,
    private onError: (error: Error) => void
  ) {}

  connect(): void {
    if (!this.config.wsUrl) {
      this.onError(new Error('WebSocket URL not configured'))
      return
    }

    try {
      this.ws = new WebSocket(this.config.wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          const transformed = Array.isArray(data) 
            ? data.map(transformApiData) 
            : [transformApiData(data)]
          this.onData(transformed)
        } catch (error) {
          this.onError(error instanceof Error ? error : new Error('Failed to parse WebSocket data'))
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.onError(new Error('WebSocket connection error'))
      }

      this.ws.onclose = () => {
        console.log('WebSocket closed')
        this.attemptReconnect()
      }
    } catch (error) {
      this.onError(error instanceof Error ? error : new Error('Failed to connect WebSocket'))
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts)
    } else {
      this.onError(new Error('Max reconnection attempts reached'))
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
}

/**
 * Main hygiene data service
 * Provides a unified interface for fetching hygiene data
 */
export class HygieneDataService {
  private config: HygieneServiceConfig
  private wsService: HygieneWebSocketService | null = null

  constructor(config: Partial<HygieneServiceConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
  }

  /**
   * Fetch hygiene data based on configured source type
   */
  async fetchData(): Promise<PageHygieneData[]> {
    switch (this.config.sourceType) {
      case 'mock':
        return fetchMockData(this.config)
      
      case 'rest':
        return fetchRestData(this.config)
      
      case 'websocket':
        throw new Error('Use subscribeToUpdates() for WebSocket data source')
      
      default:
        throw new Error(`Unknown source type: ${this.config.sourceType}`)
    }
  }

  /**
   * Subscribe to real-time updates via WebSocket
   */
  subscribeToUpdates(
    onData: (data: PageHygieneData[]) => void,
    onError: (error: Error) => void
  ): () => void {
    if (this.config.sourceType !== 'websocket') {
      throw new Error('WebSocket source type required for subscriptions')
    }

    this.wsService = new HygieneWebSocketService(this.config, onData, onError)
    this.wsService.connect()

    // Return cleanup function
    return () => {
      this.wsService?.disconnect()
      this.wsService = null
    }
  }

  /**
   * Setup polling for REST API
   */
  startPolling(
    onData: (data: PageHygieneData[]) => void,
    onError: (error: Error) => void
  ): () => void {
    const poll = async () => {
      try {
        const data = await this.fetchData()
        onData(data)
      } catch (error) {
        onError(error instanceof Error ? error : new Error('Polling failed'))
      }
    }

    // Initial fetch
    poll()

    // Setup interval
    const interval = setInterval(poll, this.config.pollingInterval)

    // Return cleanup function
    return () => clearInterval(interval)
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<HygieneServiceConfig>): void {
    this.config = { ...this.config, ...config }
  }

  /**
   * Get current configuration
   */
  getConfig(): HygieneServiceConfig {
    return { ...this.config }
  }
}

/**
 * Singleton instance for easy access
 */
export const hygieneService = new HygieneDataService()
