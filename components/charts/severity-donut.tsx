'use client'

import { useQuery } from '@tanstack/react-query'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { Card } from '@/components/ui/card'
import { DashboardService } from '@/lib/services/dashboard.service'
import { PieChart as PieIcon } from 'lucide-react'

interface SeverityData {
  name: string
  value: number
  color: string
}

interface SeverityDonutProps {
  data?: SeverityData[]
  isLoading?: boolean
}

const SEVERITY_COLORS: Record<string, string> = {
  Critical: '#ef4444',
  High: '#f97316',
  Medium: '#eab308',
  Low: '#22c55e',
}

export function SeverityDonut({ data, isLoading: propIsLoading }: SeverityDonutProps) {
  const { data: fetchedData, isLoading: queryIsLoading, error } = useQuery({
    queryKey: ['severity-distribution'],
    queryFn: () => DashboardService.getSeverityDistribution(),
    staleTime: 60 * 1000,
    retry: 1,
  })

  const defaultData = [
    { name: 'Critical', value: 104, color: SEVERITY_COLORS.Critical },
    { name: 'High', value: 186, color: SEVERITY_COLORS.High },
    { name: 'Medium', value: 240, color: SEVERITY_COLORS.Medium },
    { name: 'Low', value: 120, color: SEVERITY_COLORS.Low },
  ]

  const chartData = (data || fetchedData || defaultData) as SeverityData[]
  const isLoading = propIsLoading || queryIsLoading
  const total = chartData.reduce((sum, d) => sum + d.value, 0)

  if (isLoading) {
    return (
      <Card className="p-6 border-border">
        <div className="flex items-center justify-center h-[300px]">
          <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </Card>
    )
  }

  if (error) {
    console.error('[v0] Severity distribution error:', error)
  }

  return (
    <Card className="p-6 bg-card border-border">
      <div className="flex items-center gap-2 mb-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/10">
          <PieIcon className="h-4 w-4 text-purple-500" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-foreground">Severity Breakdown</h3>
          <p className="text-xs text-muted-foreground">{total} total alerts</p>
        </div>
      </div>
      <div className="flex flex-col items-center">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={90}
              paddingAngle={3}
              dataKey="value"
              strokeWidth={0}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color || SEVERITY_COLORS[entry.name] || '#888'} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '10px',
                fontSize: '12px',
                boxShadow: '0 4px 12px hsl(var(--foreground) / 0.1)',
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        {/* Custom legend */}
        <div className="grid grid-cols-2 gap-x-6 gap-y-2 mt-2">
          {chartData.map((entry) => (
            <div key={entry.name} className="flex items-center gap-2">
              <span
                className="h-2.5 w-2.5 rounded-full shrink-0"
                style={{ backgroundColor: entry.color || SEVERITY_COLORS[entry.name] || '#888' }}
              />
              <span className="text-xs text-muted-foreground">{entry.name}</span>
              <span className="text-xs font-semibold text-foreground ml-auto">{entry.value}</span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}
