import { Edge, Node } from 'reactflow'

export const mockActivity = [
  { ts: '10:01:12', message: 'Crawler started', level: 'info' },
  { ts: '10:01:30', message: 'Fetched https://example.com', level: 'info' },
  { ts: '10:01:33', message: 'Page analyzed: /login', level: 'success' },
  { ts: '10:01:41', message: 'JS error detected on /dashboard', level: 'warning' },
  { ts: '10:02:05', message: 'Network failure on /api/users', level: 'error' },
]

export const mockPages = [
  {
    url: 'https://example.com/',
    type: 'dashboard',
    score: 92,
    issues: [{ title: 'Missing alt text', severity: 'low', category: 'accessibility' }],
  },
  {
    url: 'https://example.com/login',
    type: 'login',
    score: 80,
    issues: [
      { title: 'JS error: Cannot read property', severity: 'high', category: 'functional' },
      { title: 'Slow load', severity: 'medium', category: 'performance' },
    ],
  },
  {
    url: 'https://example.com/users',
    type: 'list',
    score: 74,
    issues: [
      { title: 'Broken image', severity: 'medium', category: 'ui' },
      { title: 'Placeholder text', severity: 'low', category: 'content' },
    ],
  },
]

export const mockStats = {
  pagesDiscovered: 38,
  inProgress: true,
  hygieneScore: 86,
  issuesByCategory: [
    { name: 'Functional', value: 8 },
    { name: 'UI', value: 12 },
    { name: 'Performance', value: 5 },
    { name: 'Accessibility', value: 9 },
    { name: 'Content', value: 4 },
  ],
}

export const mockGraphNodes: Node[] = [
  { id: 'page-/dashboard', position: { x: 100, y: 50 }, data: { label: 'Page: /dashboard' }, type: 'input' },
  { id: 'issue-js', position: { x: 350, y: 0 }, data: { label: 'Issue: JS Error' } },
  { id: 'issue-slow', position: { x: 350, y: 100 }, data: { label: 'Issue: Slow Load' } },
]

export const mockGraphEdges: Edge[] = [
  { id: 'e1', source: 'page-/dashboard', target: 'issue-js', label: 'functional' },
  { id: 'e2', source: 'page-/dashboard', target: 'issue-slow', label: 'performance' },
]
