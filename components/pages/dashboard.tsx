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
  const { metrics, trend, isLoading: dashboardLoading } = useDashboardData()
  const { data: alertsData, isLoading: alertsLoading } = useAlerts({ limit: 10, page: 1 })

  return (
    <PageContainer>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Real-time fraud detection and alert monitoring</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Total Transactions"
            value={metrics?.total_transactions || 0}
            format="number"
            icon={<TrendingUp className="h-5 w-5" />}
            trend={metrics?.trends.alerts_change_pct}
          />
          <MetricCard
            title="Active Alerts"
            value={metrics?.active_alerts || 0}
            format="number"
            icon={<AlertCircle className="h-5 w-5" />}
            trend={metrics?.trends.alerts_change_pct}
          />
          <MetricCard
            title="High-Risk Alerts"
            value={metrics?.high_risk_alerts || 0}
            format="number"
            icon={<AlertTriangle className="h-5 w-5" />}
          />
          <MetricCard
            title="False Positive Rate"
            value={metrics?.false_positive_rate || 0}
            format="percent"
            unit="%"
            icon={<PieChartIcon className="h-5 w-5" />}
            trend={metrics?.trends.false_positive_change_pct}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <AlertsTrendChart data={trend} isLoading={dashboardLoading} />
          </div>
          <SeverityDonut isLoading={dashboardLoading} />
        </div>

        {/* Recent Alerts Table */}
        <Card className="p-6 bg-card">
          <h3 className="text-lg font-semibold mb-4 text-foreground">Recent Alerts</h3>
          <AlertsDataTable data={alertsData?.data || []} isLoading={alertsLoading} />
        </Card>
      </div>
    </PageContainer>
  )
}
