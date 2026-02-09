import { TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

interface KpiCardProps {
  title: string
  value: string
  change: string
  trend: 'up' | 'down'
}

export function KpiCard({ title, value, change, trend }: KpiCardProps) {
  const isPositive = trend === 'up'

  return (
    <Card className="bg-card border-border">
      <CardContent className="pt-6">
        <p className="text-sm text-muted-foreground mb-2">{title}</p>
        <div className="flex items-end justify-between">
          <div>
            <p className="text-3xl font-bold text-primary">{value}</p>
          </div>
          <div className="flex items-center gap-1">
            {isPositive ? (
              <TrendingUp size={18} className="text-accent" />
            ) : (
              <TrendingDown size={18} className="text-green-600" />
            )}
            <span className={`text-sm font-semibold ${isPositive ? 'text-accent' : 'text-green-600'}`}>
              {change}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
