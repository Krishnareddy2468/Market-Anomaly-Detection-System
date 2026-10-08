'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Card } from '@/components/ui/card'
import { AlertsTrend } from '@/lib/types'
import { Activity } from 'lucide-react'

interface AlertsTrendChartProps {
  data?: AlertsTrend
  isLoading?: boolean
}

export function AlertsTrendChart({ data, isLoading }: AlertsTrendChartProps) {
  if (isLoading) {
    return (
      <Card className="p-6 border-border">
        <div className="flex items-center justify-center h-[300px]">
          <div className="flex flex-col items-center gap-2">
            <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
            <p className="text-xs text-muted-foreground">Loading chart...</p>
          </div>
        </div>
      </Card>
    )
  }

  if (!data || data.timestamps.length === 0) {
    return (
      <Card className="p-6 border-border">
        <div className="flex items-center justify-center h-[300px]">
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
    <Card className="p-6 bg-card border-border">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10">
            <Activity className="h-4 w-4 text-blue-500" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">Alerts Trend</h3>
            <p className="text-xs text-muted-foreground">Last 24 hours</p>
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <defs>
            <linearGradient id="alertGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(221, 83%, 53%)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="hsl(221, 83%, 53%)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
          <XAxis
            dataKey="timestamp"
            stroke="hsl(var(--muted-foreground))"
            fontSize={11}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="hsl(var(--muted-foreground))"
            fontSize={11}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'hsl(var(--card))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '10px',
              fontSize: '12px',
              boxShadow: '0 4px 12px hsl(var(--foreground) / 0.1)',
            }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="hsl(221, 83%, 53%)"
            strokeWidth={2}
            fill="url(#alertGradient)"
            dot={false}
            activeDot={{ r: 5, fill: 'hsl(221, 83%, 53%)', stroke: 'hsl(var(--card))', strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  )
}
