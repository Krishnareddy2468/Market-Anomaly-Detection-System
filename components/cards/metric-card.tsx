import { Card } from '@/components/ui/card'
import { ReactNode } from 'react'
import { formatNumber, formatPercent } from '@/lib/utils/formatters'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: number | string
  icon?: ReactNode
  trend?: number
  unit?: string
  format?: 'number' | 'percent' | 'currency'
  className?: string
}

export function MetricCard({ title, value, icon, trend, unit, format = 'number' }: MetricCardProps) {
  const isPositive = trend ? trend > 0 : false

  let formattedValue = value.toString()
  if (typeof value === 'number') {
    if (format === 'percent') {
      formattedValue = formatPercent(value)
    } else if (format === 'number') {
      formattedValue = formatNumber(value)
    } else if (format === 'currency') {
      formattedValue = `$${formatNumber(value)}`
    }
  }

  return (
    <Card className="p-6 bg-card text-card-foreground border-border hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <div className="mt-3 flex items-baseline gap-2">
            <p className="text-3xl font-bold">{formattedValue}</p>
            {unit && <span className="text-sm text-muted-foreground">{unit}</span>}
          </div>
          {trend !== undefined && (
            <div className="mt-3 flex items-center gap-1">
              {isPositive ? (
                <TrendingUp className="h-4 w-4 text-red-500" />
              ) : (
                <TrendingDown className="h-4 w-4 text-green-500" />
              )}
              <span className={`text-xs font-medium ${isPositive ? 'text-red-600' : 'text-green-600'}`}>
                {Math.abs(trend)}% {isPositive ? 'increase' : 'decrease'}
              </span>
            </div>
          )}
        </div>
        {icon && <div className="text-muted-foreground">{icon}</div>}
      </div>
    </Card>
  )
}
