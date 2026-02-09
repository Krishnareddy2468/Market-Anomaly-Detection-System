import { AlertSeverity } from '../types'
import { formatTimeRelative, formatTimeAbsolute, formatTimeTime } from './format-time'

export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(amount)
}

export const formatDate = (dateString: string): string => {
  // Try to use the absolute format for consistency with the provided utilities
  try {
    return formatTimeAbsolute(dateString)
  } catch (error) {
    console.error('[v0] Error formatting date:', error, dateString)
    // Fallback to relative format if absolute fails
    return formatTimeRelative(dateString)
  }
}

export const formatTime = (dateString: string): string => {
  try {
    return formatTimeTime(dateString)
  } catch (error) {
    console.error('[v0] Error formatting time:', error, dateString)
    return 'N/A'
  }
}

export const formatPercent = (value: number, decimals: number = 1): string => {
  return `${value.toFixed(decimals)}%`
}

export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('en-US').format(value)
}

export const formatRiskScore = (score: number): string => {
  return `${Math.min(Math.round(score), 100)}`
}

export const getSeverityColor = (severity: AlertSeverity | string): string => {
  switch (severity) {
    case 'CRITICAL':
      return 'text-red-600 bg-red-50'
    case 'HIGH':
      return 'text-orange-600 bg-orange-50'
    case 'MEDIUM':
      return 'text-yellow-600 bg-yellow-50'
    case 'LOW':
      return 'text-green-600 bg-green-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

export const getSeverityBadgeClass = (severity: AlertSeverity | string): string => {
  switch (severity) {
    case 'CRITICAL':
      return 'bg-red-100 text-red-800'
    case 'HIGH':
      return 'bg-orange-100 text-orange-800'
    case 'MEDIUM':
      return 'bg-yellow-100 text-yellow-800'
    case 'LOW':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

export const getStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'ACTIVE':
      return 'bg-red-100 text-red-800'
    case 'INVESTIGATING':
      return 'bg-blue-100 text-blue-800'
    case 'RESOLVED':
      return 'bg-green-100 text-green-800'
    case 'FALSE_POSITIVE':
      return 'bg-purple-100 text-purple-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

export const truncateAddress = (address: string, length: number = 10): string => {
  if (address.length <= length) return address
  return `${address.slice(0, length / 2)}...${address.slice(-length / 2)}`
}
