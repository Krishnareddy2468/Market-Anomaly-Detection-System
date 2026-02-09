import { Badge } from '@/components/ui/badge'
import { AlertSeverity } from '@/lib/types'
import { getSeverityBadgeClass } from '@/lib/utils/formatters'

interface SeverityBadgeProps {
  severity: AlertSeverity | string
  className?: string
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const displayText = severity.charAt(0) + severity.slice(1).toLowerCase()

  return (
    <Badge className={getSeverityBadgeClass(severity)}>
      {displayText}
    </Badge>
  )
}

interface StatusBadgeProps {
  status: string
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const getStatusColor = (s: string) => {
    switch (s) {
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

  const displayText = status.replace(/_/g, ' ').charAt(0) + status.slice(1).toLowerCase().replace(/_/g, ' ')

  return (
    <Badge className={getStatusColor(status)}>
      {displayText}
    </Badge>
  )
}
