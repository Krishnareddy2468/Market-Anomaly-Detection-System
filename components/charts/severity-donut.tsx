'use client'

import { useQuery } from '@tanstack/react-query'
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts'
import { Card } from '@/components/ui/card'
import { DashboardService } from '@/lib/services/dashboard.service'

interface SeverityData {
  name: string
  value: number
  color: string
}

interface SeverityDonutProps {
  data?: SeverityData[]
  isLoading?: boolean
}

export function SeverityDonut({ data, isLoading: propIsLoading }: SeverityDonutProps) {
  const { data: fetchedData, isLoading: queryIsLoading, error } = useQuery({
    queryKey: ['severity-distribution'],
    queryFn: () => DashboardService.getSeverityDistribution(),
    staleTime: 60 * 1000,
    retry: 1,
  })

  const defaultData = [
    { name: 'High', value: 35, color: 'hsl(0, 84%, 60%)' },
    { name: 'Medium', value: 45, color: 'hsl(54, 92%, 50%)' },
    { name: 'Low', value: 20, color: 'hsl(120, 73%, 75%)' },
  ]

  const chartData = (data || fetchedData || defaultData) as SeverityData[]
  const isLoading = propIsLoading || queryIsLoading

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <p className="text-sm text-muted-foreground">Loading chart...</p>
        </div>
      </Card>
    )
  }

  if (error) {
    console.error('[v0] Severity distribution error:', error)
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <p className="text-sm text-muted-foreground">Failed to load chart. Using cached data.</p>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-6 bg-card">
      <h3 className="text-lg font-semibold mb-4 text-foreground">Alerts by Severity</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={80}
            outerRadius={120}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData && chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}
