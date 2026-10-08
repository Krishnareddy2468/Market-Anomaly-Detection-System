import { Badge } from '@/components/ui/badge'
import { AlertSeverity } from '@/lib/types'
import { getSeverityBadgeClass } from '@/lib/utils/formatters'

interface SeverityBadgeProps {
  severity: AlertSeverity | string
  className?: string
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const displayText = severity.charAt(0) + severity.slice(1).toLowerCase()

  const colorMap: Record<string, string> = {
    CRITICAL: 'bg-red-500/15 text-red-500 border-red-500/20',
    HIGH: 'bg-orange-500/15 text-orange-500 border-orange-500/20',
    MEDIUM: 'bg-yellow-500/15 text-yellow-600 border-yellow-500/20',
    LOW: 'bg-emerald-500/15 text-emerald-500 border-emerald-500/20',
  }

  return (
    <Badge className={`${colorMap[severity] || 'bg-muted text-muted-foreground'} border text-[10px] font-semibold px-2 py-0.5 ${className || ''}`}>
      {displayText}
    </Badge>
  )
}

interface StatusBadgeProps {
  status: string
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const colorMap: Record<string, string> = {
    ACTIVE: 'bg-red-500/15 text-red-500 border-red-500/20',
    INVESTIGATING: 'bg-blue-500/15 text-blue-500 border-blue-500/20',
    RESOLVED: 'bg-emerald-500/15 text-emerald-500 border-emerald-500/20',
    FALSE_POSITIVE: 'bg-purple-500/15 text-purple-500 border-purple-500/20',
  }

  const displayText = status.replace(/_/g, ' ').charAt(0) + status.slice(1).toLowerCase().replace(/_/g, ' ')

  return (
    <Badge className={`${colorMap[status] || 'bg-muted text-muted-foreground'} border text-[10px] font-semibold px-2 py-0.5 ${className || ''}`}>
      {displayText}
    </Badge>
  )
}
