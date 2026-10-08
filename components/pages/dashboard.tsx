'use client'

import { useDashboardData } from '@/lib/hooks/useDashboard'
import { useAlerts } from '@/lib/hooks/useAlerts'
import { MetricCard } from '@/components/cards/metric-card'
import { AlertsTrendChart } from '@/components/charts/alerts-trend-chart'
import { SeverityDonut } from '@/components/charts/severity-donut'
import { AlertsDataTable } from '@/components/tables/alerts-data-table'
import { Card } from '@/components/ui/card'
import { AlertCircle, TrendingUp, AlertTriangle, PieChart as PieChartIcon } from 'lucide-react'
import { PageContainer } from '@/components/layout/page-container'

export function Dashboard() {
  const { metrics, trend, isLoading: dashboardLoading } = useDashboardData('7d')
  const { data: alertsData, isLoading: alertsLoading } = useAlerts({ limit: 10, page: 1 })

  return (
    <PageContainer>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground tracking-tight">Dashboard</h1>
            <p className="text-sm text-muted-foreground mt-0.5">Real-time fraud detection overview</p>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="text-xs font-medium text-muted-foreground">System Active</span>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Total Transactions"
            value={metrics?.total_transactions || 0}
            format="number"
            icon={<TrendingUp className="h-5 w-5" />}
            accentColor="bg-blue-500/10 text-blue-500"
          />
          <MetricCard
            title="Active Alerts"
            value={metrics?.active_alerts || 0}
            format="number"
            icon={<AlertCircle className="h-5 w-5" />}
            accentColor="bg-amber-500/10 text-amber-500"
          />
          <MetricCard
            title="High-Risk Alerts"
            value={metrics?.high_risk_alerts || 0}
            format="number"
            icon={<AlertTriangle className="h-5 w-5" />}
            accentColor="bg-red-500/10 text-red-500"
          />
          <MetricCard
            title="False Positive Rate"
            value={metrics?.false_positive_rate || 0}
            format="percent"
            unit="%"
            icon={<PieChartIcon className="h-5 w-5" />}
            accentColor="bg-emerald-500/10 text-emerald-500"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <AlertsTrendChart data={trend} isLoading={dashboardLoading} range="7d" />
          </div>
          <SeverityDonut isLoading={dashboardLoading} />
        </div>

        {/* Recent Alerts Table */}
        <Card className="p-6 bg-card border-border">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-500/10">
                <AlertCircle className="h-4 w-4 text-red-500" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-foreground">Recent Alerts</h3>
                <p className="text-xs text-muted-foreground">Latest flagged transactions</p>
              </div>
            </div>
          </div>
          <AlertsDataTable data={alertsData?.data || []} isLoading={alertsLoading} />
        </Card>
      </div>
    </PageContainer>
  )
}
