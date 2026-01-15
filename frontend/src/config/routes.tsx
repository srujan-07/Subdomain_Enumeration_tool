import { NewScan } from '../pages/NewScan'
import { ActiveScans } from '../pages/ActiveScans'
import { ScanHistory } from '../pages/ScanHistory'
import { KnowledgeGraph } from '../pages/KnowledgeGraph'
import { HygieneDashboard } from '../pages/HygieneDashboard'
import { PageDetailView } from '../pages/PageDetailView'

/**
 * Navigation item configuration
 */
export interface NavItem {
  key: string
  label: string
  path: string
  icon?: string
}

/**
 * Route configuration
 */
export interface RouteConfig {
  path: string
  element: React.ComponentType
  exact?: boolean
}

/**
 * Centralized navigation configuration
 * Single source of truth for all app navigation
 */
export const NAV_ITEMS: NavItem[] = [
  { key: 'new', label: 'New Scan', path: '/new' },
  { key: 'active', label: 'Active Scans', path: '/active' },
  { key: 'history', label: 'Scan History', path: '/history' },
  { key: 'graph', label: 'Defect Knowledge Graph', path: '/graph' },
  { key: 'hygiene', label: 'Hygiene Dashboard', path: '/hygiene' },
  { key: 'settings', label: 'Settings', path: '/settings' },
]

/**
 * Centralized route configuration
 */
export const ROUTES: RouteConfig[] = [
  { path: '/new', element: NewScan },
  { path: '/active', element: ActiveScans },
  { path: '/history', element: ScanHistory },
  { path: '/graph', element: KnowledgeGraph },
  { path: '/hygiene', element: HygieneDashboard },
  { path: '/pages', element: PageDetailView },
]

/**
 * Default route redirect path
 */
export const DEFAULT_ROUTE = '/new'

/**
 * Map pathname to nav key
 */
export function getNavKeyFromPath(pathname: string): string {
  const item = NAV_ITEMS.find(item => item.path === pathname)
  if (item) return item.key
  
  // Fallback to first segment
  const firstSegment = pathname.split('/')[1]
  return firstSegment || 'new'
}

/**
 * Map nav key to path
 */
export function getPathFromNavKey(key: string): string {
  const item = NAV_ITEMS.find(item => item.key === key)
  return item?.path || DEFAULT_ROUTE
}
