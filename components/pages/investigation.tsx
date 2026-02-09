'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { AlertTriangle, TrendingUp } from 'lucide-react'

const historicalData = [
  { date: '5 days ago', score: 15 },
  { date: '4 days ago', score: 18 },
  { date: '3 days ago', score: 22 },
  { date: '2 days ago', score: 25 },
  { date: 'Yesterday', score: 35 },
  { date: 'Today', score: 94 },
]

const transactionDetails = [
  { label: 'Transaction ID', value: 'TXN-2024-001234' },
  { label: 'Timestamp', value: '2024-02-09 14:32:18 UTC' },
  { label: 'Amount', value: '$45,230.00' },
  { label: 'Currency', value: 'USD' },
  { label: 'Source', value: 'Account #42521' },
  { label: 'Destination', value: 'Account #8839' },
  { label: 'Channel', value: 'API' },
  { label: 'IP Address', value: '192.168.1.105' },
]

const featureDeviations = [
  { feature: 'Transaction Amount', deviation: '+340%', risk: 'Very High' },
  { feature: 'Time of Day', deviation: 'Unusual Pattern', risk: 'High' },
  { feature: 'Frequency', deviation: '+8x Normal Rate', risk: 'High' },
  { feature: 'Geographic Location', deviation: 'New Country', risk: 'Medium' },
  { feature: 'Device Fingerprint', deviation: 'New Device', risk: 'Medium' },
]

export function InvestigationPage() {
  return (
    <div className="p-6 space-y-6 ml-20 md:ml-64">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-1 space-y-4">
          {/* Alert Summary */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-primary flex items-center gap-2">
                <AlertTriangle size={20} className="text-accent" />
                Alert Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Alert ID</p>
                <p className="font-semibold text-foreground">ALT-001</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Entity</p>
                <p className="font-semibold text-foreground">User #42521</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <p className="font-semibold text-foreground">Active Investigation</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-2">Risk Score</p>
                <div className="flex items-end gap-2">
                  <Progress value={94} className="flex-1" />
                  <span className="font-bold text-accent text-lg">94</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <Card className="bg-card border-border">
            <CardContent className="pt-6 space-y-2">
              <Button className="w-full bg-accent hover:bg-accent/90 text-foreground">Mark as Fraud</Button>
              <Button variant="outline" className="w-full border-border bg-transparent">
                Mark as False Positive
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right Column */}
        <div className="lg:col-span-2 space-y-4">
          {/* Transaction Details */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-primary">Transaction Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {transactionDetails.map((item) => (
                  <div key={item.label}>
                    <p className="text-xs text-muted-foreground uppercase">{item.label}</p>
                    <p className="font-mono text-sm text-foreground">{item.value}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Feature Deviations */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-primary">Feature Deviations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {featureDeviations.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-secondary/30 rounded-lg">
                    <div>
                      <p className="font-medium text-foreground text-sm">{item.feature}</p>
                      <p className="text-xs text-muted-foreground">{item.deviation}</p>
                    </div>
                    <span
                      className={`text-xs font-semibold px-2 py-1 rounded ${
                        item.risk === 'Very High'
                          ? 'bg-accent/20 text-accent'
                          : item.risk === 'High'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-green-100 text-green-700'
                      }`}
                    >
                      {item.risk}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Historical Chart */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-primary flex items-center gap-2">
            <TrendingUp size={20} />
            Historical Behavior
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={historicalData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(200 8% 88%)" />
              <XAxis dataKey="date" stroke="hsl(200 5% 45%)" style={{ fontSize: '12px' }} />
              <YAxis stroke="hsl(200 5% 45%)" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(0 0% 100%)',
                  border: '1px solid hsl(200 8% 88%)',
                  borderRadius: '6px',
                }}
              />
              <Line type="monotone" dataKey="score" stroke="hsl(0 84% 60%)" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Notes Section */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-primary">Add Notes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Add investigation notes here..."
            className="bg-input border-border text-foreground min-h-32"
          />
          <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
            Submit Decision
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
