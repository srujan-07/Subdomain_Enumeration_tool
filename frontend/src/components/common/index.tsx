import React from 'react'

/**
 * Reusable loading spinner component
 */
export const LoadingSpinner: React.FC<{ message?: string; size?: 'sm' | 'md' | 'lg' }> = ({ 
  message = 'Loading...', 
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
  }

  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className={`animate-spin rounded-full border-b-2 border-slate-900 mx-auto mb-4 ${sizeClasses[size]}`} />
        <p className="text-slate-600">{message}</p>
      </div>
    </div>
  )
}

/**
 * Reusable error message component
 */
export const ErrorMessage: React.FC<{ title?: string; message: string; onRetry?: () => void }> = ({ 
  title = 'Error', 
  message,
  onRetry 
}) => {
  return (
    <div className="card p-6">
      <div className="text-center text-red-600">
        <p className="font-semibold text-lg mb-2">{title}</p>
        <p className="text-sm mb-4">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  )
}

/**
 * Reusable empty state component
 */
export const EmptyState: React.FC<{ message: string; icon?: React.ReactNode }> = ({ 
  message, 
  icon 
}) => {
  return (
    <div className="text-center py-8 text-slate-500">
      {icon && <div className="mb-4 flex justify-center">{icon}</div>}
      <p>{message}</p>
    </div>
  )
}

/**
 * Reusable statistic card component
 */
interface StatCardProps {
  label: string
  value: string | number
  valueColor?: string
  icon?: React.ReactNode
  trend?: {
    value: number
    direction: 'up' | 'down'
  }
}

export const StatCard: React.FC<StatCardProps> = ({ 
  label, 
  value, 
  valueColor = 'text-slate-900',
  icon,
  trend 
}) => {
  return (
    <div className="card p-4">
      <div className="flex items-start justify-between mb-1">
        <div className="text-sm text-slate-600">{label}</div>
        {icon && <div className="text-slate-400">{icon}</div>}
      </div>
      <div className={`text-3xl font-bold ${valueColor}`}>{value}</div>
      {trend && (
        <div className={`text-xs mt-2 ${trend.direction === 'up' ? 'text-green-600' : 'text-red-600'}`}>
          {trend.direction === 'up' ? '↑' : '↓'} {Math.abs(trend.value)}%
        </div>
      )}
    </div>
  )
}

/**
 * Reusable badge component
 */
interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md' | 'lg'
}

export const Badge: React.FC<BadgeProps> = ({ 
  children, 
  variant = 'default',
  size = 'md' 
}) => {
  const variantClasses = {
    default: 'bg-slate-100 text-slate-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
  }

  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  }

  return (
    <span className={`inline-block rounded-full font-bold ${variantClasses[variant]} ${sizeClasses[size]}`}>
      {children}
    </span>
  )
}

/**
 * Reusable section header component
 */
interface SectionHeaderProps {
  title: string
  subtitle?: string
  action?: React.ReactNode
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({ 
  title, 
  subtitle, 
  action 
}) => {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 mb-2">{title}</h1>
        {subtitle && <p className="text-slate-600">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
