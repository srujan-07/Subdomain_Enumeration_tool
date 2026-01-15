import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { ROUTES, DEFAULT_ROUTE } from './config/routes'

/**
 * Main application component
 * Simplified routing with configuration-driven approach
 */
export const App: React.FC = () => {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <Routes>
          <Route path="/" element={<Navigate to={DEFAULT_ROUTE} replace />} />
          {ROUTES.map(({ path, element: Element }) => (
            <Route key={path} path={path} element={<Element />} />
          ))}
          <Route path="/settings" element={
            <div className="card p-6">
              <h2 className="text-xl font-bold mb-2">Settings</h2>
              <p className="text-slate-600">Coming Soon</p>
            </div>
          } />
          <Route path="*" element={<Navigate to={DEFAULT_ROUTE} replace />} />
        </Routes>
      </main>
    </div>
  )
}
