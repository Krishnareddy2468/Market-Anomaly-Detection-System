'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Card } from '@/components/ui/card'
import { AlertsTrend } from '@/lib/types'

interface AlertsTrendChartProps {
  data?: AlertsTrend
  isLoading?: boolean
}

export function AlertsTrendChart({ data, isLoading }: AlertsTrendChartProps) {
  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <p className="text-sm text-muted-foreground">Loading chart...</p>
        </div>
      </Card>
    )
  }

  if (!data || data.timestamps.length === 0) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <p className="text-sm text-muted-foreground">No data available</p>
        </div>
      </Card>
    )
  }

  const chartData = data.timestamps.map((timestamp, index) => ({
    timestamp,
    value: data.values[index],
  }))

  return (
    <Card className="p-6 bg-card">
      <h3 className="text-lg font-semibold mb-4 text-foreground">Alerts Trend (24h)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="timestamp" stroke="var(--muted-foreground)" />
          <YAxis stroke="var(--muted-foreground)" />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
            }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="var(--accent)"
            strokeWidth={2}
            dot={{ fill: 'var(--accent)', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  )
}
