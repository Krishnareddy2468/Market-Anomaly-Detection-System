export const ALERT_SEVERITY_OPTIONS = [
  { label: 'All', value: 'ALL' },
  { label: 'Critical', value: 'CRITICAL' },
  { label: 'High', value: 'HIGH' },
  { label: 'Medium', value: 'MEDIUM' },
  { label: 'Low', value: 'LOW' },
]

export const ALERT_STATUS_OPTIONS = [
  { label: 'All', value: 'ALL' },
  { label: 'Active', value: 'ACTIVE' },
  { label: 'Investigating', value: 'INVESTIGATING' },
  { label: 'Resolved', value: 'RESOLVED' },
  { label: 'False Positive', value: 'FALSE_POSITIVE' },
]

export const DECISION_OPTIONS = [
  { label: 'Fraud', value: 'FRAUD', color: 'bg-red-100 text-red-800' },
  { label: 'Legitimate', value: 'LEGITIMATE', color: 'bg-green-100 text-green-800' },
  { label: 'Review', value: 'REVIEW', color: 'bg-yellow-100 text-yellow-800' },
]

export const DEFAULT_PAGE_SIZE = 10
export const DEFAULT_TREND_RANGE = '24h'

export const SEVERITY_LEVELS = {
  CRITICAL: 4,
  HIGH: 3,
  MEDIUM: 2,
  LOW: 1,
}

export const STATUS_PRIORITIES = {
  ACTIVE: 1,
  INVESTIGATING: 2,
  RESOLVED: 3,
  FALSE_POSITIVE: 4,
}
