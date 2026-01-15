import React from 'react'
import { NavLink } from 'react-router-dom'
import { NAV_ITEMS } from '../config/routes'

/**
 * Sidebar navigation component
 * Simplified with configuration-driven approach
 */
export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-white border-r border-slate-200 h-screen flex flex-col">
      <div className="px-4 py-5 text-xl font-bold text-slate-900">AutoTest</div>
      <nav className="flex-1 px-2 space-y-1">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            className={({ isActive }) =>
              `block w-full text-left px-3 py-2 rounded-lg font-medium transition-colors ${
                isActive ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="px-4 py-4 text-xs text-slate-500">Autonomous Web Testing Platform</div>
    </aside>
  )
}
