import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LoadingSpinner, ErrorMessage } from '../components/common'

export const NewScan: React.FC = () => {
  const navigate = useNavigate()
  const [url, setUrl] = useState('https://example.com')
  const [options, setOptions] = useState({ maxPages: 50, concurrency: 10, headful: false })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleStartScan = async () => {
    try {
      setLoading(true)
      setError(null)

      // Validate URL
      if (!url || !url.startsWith('http')) {
        throw new Error('Please enter a valid URL (starting with http:// or https://)')
      }

      // Call backend API
      const response = await fetch('http://localhost:8000/api/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url,
          depth: 2,
          mode: 'full',
          wayback: true,
          bruteforce: false,
          validate_ssl: true,
          maxPages: options.maxPages,
          concurrency: options.concurrency,
          headful: options.headful,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.status === 'started' || data.status === 'completed') {
        // Navigate to active scans page
        navigate('/active')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start scan'
      setError(errorMessage)
      console.error('Scan error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <LoadingSpinner message="Starting scan..." />
  }

  if (error) {
    return (
      <ErrorMessage
        title="Scan Error"
        message={error}
        onRetry={() => setError(null)}
      />
    )
  }

  return (
    <div className="card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Start a New Scan</h2>
          <p className="text-slate-500 text-sm">Set your base URL and scan options.</p>
        </div>
        <button
          onClick={handleStartScan}
          disabled={loading}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Scanning...' : 'Start Scan'}
        </button>
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Base URL *</label>
        <input
          className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-900"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://your-site.com"
          disabled={loading}
        />
        <p className="text-xs text-slate-500">Example: https://cvr.ac.in</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="space-y-2">
          <label className="text-sm font-medium">Max Pages</label>
          <input
            type="number"
            className="w-full border rounded-lg px-3 py-2"
            value={options.maxPages}
            onChange={(e) => setOptions((o) => ({ ...o, maxPages: Number(e.target.value) }))}
            disabled={loading}
            min="1"
            max="1000"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Crawler Concurrency</label>
          <input
            type="number"
            className="w-full border rounded-lg px-3 py-2"
            value={options.concurrency}
            onChange={(e) => setOptions((o) => ({ ...o, concurrency: Number(e.target.value) }))}
            disabled={loading}
            min="1"
            max="50"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Browser Mode</label>
          <select
            className="w-full border rounded-lg px-3 py-2"
            value={options.headful ? 'headful' : 'headless'}
            onChange={(e) => setOptions((o) => ({ ...o, headful: e.target.value === 'headful' }))}
            disabled={loading}
          >
            <option value="headless">Headless (Faster)</option>
            <option value="headful">Headful (With Browser)</option>
          </select>
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">What This Scan Does:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>✓ Crawls all discoverable pages and URLs</li>
          <li>✓ Analyzes JavaScript files for API endpoints</li>
          <li>✓ Tests for common paths and files</li>
          <li>✓ Checks historical URLs from Wayback Machine</li>
          <li>✓ Validates all discovered URLs</li>
          <li>✓ Generates quality hygiene report</li>
        </ul>
      </div>
    </div>
  )
}
