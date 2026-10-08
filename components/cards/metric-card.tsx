import { Card } from '@/components/ui/card'
import { ReactNode } from 'react'
import { formatCurrency, formatNumber, formatPercent } from '@/lib/utils/formatters'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { useCurrency } from '@/lib/contexts/currency-context'

interface MetricCardProps {
  title: string
  value: number | string
  icon?: ReactNode
  trend?: number
  unit?: string
  format?: 'number' | 'percent' | 'currency'
  className?: string
  accentColor?: string
}

export function MetricCard({ title, value, icon, trend, unit, format = 'number', accentColor }: MetricCardProps) {
  const isPositive = trend ? trend > 0 : false
  const { currency } = useCurrency()

  let formattedValue = value.toString()
  if (typeof value === 'number') {
    if (format === 'percent') {
      formattedValue = formatPercent(value)
    } else if (format === 'number') {
      formattedValue = formatNumber(value)
    } else if (format === 'currency') {
      formattedValue = formatCurrency(value, 'INR', currency)
    }
  }

  const colorClass = accentColor || 'bg-primary/10 text-primary'

  return (
    <Card className="group relative overflow-hidden p-5 bg-card text-card-foreground border-border hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{title}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <p className="text-2xl font-bold tracking-tight">{formattedValue}</p>
            {unit && <span className="text-sm text-muted-foreground">{unit}</span>}
          </div>
          {trend !== undefined && trend !== 0 && (
            <div className="mt-2 flex items-center gap-1.5">
              {isPositive ? (
                <div className="flex items-center gap-1 text-red-500">
                  <TrendingUp className="h-3.5 w-3.5" />
                  <span className="text-xs font-semibold">{Math.abs(trend)}%</span>
                </div>
              ) : (
                <div className="flex items-center gap-1 text-emerald-500">
                  <TrendingDown className="h-3.5 w-3.5" />
                  <span className="text-xs font-semibold">{Math.abs(trend)}%</span>
                </div>
              )}
              <span className="text-xs text-muted-foreground">vs last period</span>
            </div>
          )}
        </div>
        {icon && (
          <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${colorClass} shrink-0`}>
            {icon}
          </div>
        )}
      </div>
      {/* Subtle accent bar at bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
    </Card>
  )
}
