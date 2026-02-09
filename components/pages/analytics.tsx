'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const modelPerformanceMetrics = [
  { label: 'Precision', value: 94.2, unit: '%' },
  { label: 'Recall', value: 87.5, unit: '%' },
  { label: 'F1 Score', value: 90.7, unit: '%' },
  { label: 'Alert Volume', value: '2.4K', unit: 'daily' },
]

const alertVolumeData = [
  { day: 'Mon', alerts: 280, frauds: 24 },
  { day: 'Tue', alerts: 320, frauds: 28 },
  { day: 'Wed', alerts: 290, frauds: 19 },
  { day: 'Thu', alerts: 350, frauds: 32 },
  { day: 'Fri', alerts: 410, frauds: 38 },
  { day: 'Sat', alerts: 380, frauds: 35 },
  { day: 'Sun', alerts: 320, frauds: 26 },
]

const modelAccuracyData = [
  { model: 'v1.0', accuracy: 82.5 },
  { model: 'v1.5', accuracy: 85.3 },
  { model: 'v2.0', accuracy: 89.1 },
  { model: 'v2.5', accuracy: 92.8 },
  { model: 'v3.0', accuracy: 94.2 },
]

export function AnalyticsPage() {
  return (
    <div className="p-6 space-y-6 ml-20 md:ml-64">
      {/* Model Performance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {modelPerformanceMetrics.map((metric, idx) => (
          <Card key={idx} className="bg-card border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-muted-foreground font-medium">{metric.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-2">
                <span className="text-3xl font-bold text-primary">{metric.value}</span>
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
              <p className="text-3xl font-bold text-primary">215</p>
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
              <p className="text-3xl font-bold text-orange-600">23</p>
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
              <p className="text-3xl font-bold text-green-600">90.3%</p>
              <p className="text-sm text-muted-foreground">Fraud cases caught</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
