'use client'

import { useConfusionMatrix, useDetectionRate, useModelPerformance, usePerformanceMetrics, useAnalyticsTrends } from '@/lib/hooks/useAnalytics'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { PageContainer } from '@/components/layout/page-container'

export function AnalyticsPage() {
  const { data: metrics } = usePerformanceMetrics()
  const { data: volume } = useAnalyticsTrends()
  const { data: modelPerf } = useModelPerformance()
  const { data: confusion } = useConfusionMatrix()
  const { data: detection } = useDetectionRate()

  const modelPerformanceMetrics = [
    { label: 'Precision', value: metrics?.precision ?? 0, unit: '%' },
    { label: 'Recall', value: metrics?.recall ?? 0, unit: '%' },
    { label: 'F1 Score', value: metrics?.f1_score ?? 0, unit: '%' },
    { label: 'Alert Volume', value: metrics?.alert_volume_daily ?? 0, unit: 'daily' },
  ]

  const alertVolumeData =
    volume?.labels.map((label, index) => ({
      day: label,
      alerts: volume.alerts[index] ?? 0,
      frauds: volume.frauds[index] ?? 0,
    })) || []

  const modelAccuracyData =
    modelPerf?.versions.map((version, index) => ({
      model: version,
      accuracy: modelPerf.accuracy[index] ?? 0,
    })) || []

  return (
    <PageContainer>
      <div className="space-y-6">
      {/* Model Performance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {modelPerformanceMetrics.map((metric, idx) => (
          <Card key={idx} className="bg-card border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-muted-foreground font-medium">{metric.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-2">
                <span className="text-3xl font-bold text-primary">{typeof metric.value === 'number' ? metric.value.toFixed(1) : metric.value}</span>
                <span className="text-sm text-muted-foreground">{metric.unit}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alert Volume Over Time */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-primary">Alert Volume & Fraud Detection</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={alertVolumeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(200 8% 88%)" />
                <XAxis dataKey="day" stroke="hsl(200 5% 45%)" style={{ fontSize: '12px' }} />
                <YAxis stroke="hsl(200 5% 45%)" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(0 0% 100%)',
                    border: '1px solid hsl(200 8% 88%)',
                    borderRadius: '6px',
                  }}
                />
                <Bar dataKey="alerts" fill="hsl(200 60% 50%)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="frauds" fill="hsl(0 84% 60%)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Model Accuracy Progression */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-primary">Model Accuracy Over Versions</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={modelAccuracyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(200 8% 88%)" />
                <XAxis dataKey="model" stroke="hsl(200 5% 45%)" style={{ fontSize: '12px' }} />
                <YAxis stroke="hsl(200 5% 45%)" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(0 0% 100%)',
                    border: '1px solid hsl(200 8% 88%)',
                    borderRadius: '6px',
                  }}
                />
                <Line type="monotone" dataKey="accuracy" stroke="hsl(184 100% 45%)" strokeWidth={3} dot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground font-medium">True Positives (7 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-3xl font-bold text-primary">{confusion?.true_positives ?? 0}</p>
              <p className="text-sm text-muted-foreground">Correctly identified frauds</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground font-medium">False Positives (7 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-3xl font-bold text-orange-600">{confusion?.false_positives ?? 0}</p>
              <p className="text-sm text-muted-foreground">Legitimate flagged as fraud</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-sm text-muted-foreground font-medium">Detection Rate (7 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-3xl font-bold text-green-600">{(detection?.average ?? 0).toFixed(2)}%</p>
              <p className="text-sm text-muted-foreground">Fraud cases caught</p>
            </div>
          </CardContent>
        </Card>
      </div>
      </div>
    </PageContainer>
  )
}
