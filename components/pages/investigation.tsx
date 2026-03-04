'use client'

import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { AlertsService } from '@/lib/services/alerts.service'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { AlertTriangle, TrendingUp } from 'lucide-react'
import { formatCurrency, formatDate } from '@/lib/utils/formatters'
import { useCurrency } from '@/lib/contexts/currency-context'

export function InvestigationPage() {
  const [inputAlertId, setInputAlertId] = useState('ALT-1000')
  const [activeAlertId, setActiveAlertId] = useState('ALT-1000')
  const [note, setNote] = useState('')
  const { currency: displayCurrency } = useCurrency()

  useEffect(() => {
    const selected = localStorage.getItem('selected_alert_id')
    if (selected) {
      setInputAlertId(selected)
      setActiveAlertId(selected)
    }
  }, [])

  const {
    data: investigation,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['investigation', activeAlertId],
    queryFn: () => AlertsService.getInvestigation(activeAlertId),
    enabled: !!activeAlertId,
  })

  const noteMutation = useMutation({
    mutationFn: () => AlertsService.addInvestigationNote(activeAlertId, note, 'analyst-001'),
    onSuccess: async () => {
      setNote('')
      await refetch()
    },
  })

  const decisionMutation = useMutation({
    mutationFn: (decision: 'FRAUD' | 'LEGITIMATE' | 'REVIEW') =>
      AlertsService.submitDecision(activeAlertId, {
        decision,
        notes: note || undefined,
        analyst_id: 'analyst-001',
      }),
    onSuccess: async () => {
      await refetch()
    },
  })

  const transactionDetails = useMemo(
    () =>
      investigation?.transaction
        ? [
            { label: 'Transaction ID', value: investigation.transaction.transaction_id },
            { label: 'Timestamp', value: formatDate(investigation.transaction.timestamp) },
            {
              label: 'Amount',
              value: formatCurrency(
                investigation.transaction.amount,
                investigation.transaction.currency,
                displayCurrency,
              ),
            },
            { label: 'Display Currency', value: displayCurrency },
            { label: 'Source Currency', value: investigation.transaction.currency || 'INR' },
            { label: 'Source', value: investigation.transaction.source_account },
            { label: 'Destination', value: investigation.transaction.destination_account },
            { label: 'Channel', value: investigation.transaction.channel || '-' },
            { label: 'IP Address', value: investigation.transaction.ip_address || '-' },
          ]
        : [],
    [displayCurrency, investigation],
  )

  const historicalData = (investigation?.historical_behavior || []).map((item, idx) => ({
    date: item.model || `Point ${idx + 1}`,
    score: item.score,
  }))

  const riskPillClass = (risk: string) => {
    if (risk === 'VERY_HIGH') return 'bg-red-100 text-red-700'
    if (risk === 'HIGH') return 'bg-orange-100 text-orange-700'
    if (risk === 'MEDIUM') return 'bg-yellow-100 text-yellow-700'
    return 'bg-green-100 text-green-700'
  }

  return (
    <div className="p-6 space-y-6">
      <Card className="bg-card border-border">
        <CardContent className="pt-6 flex flex-col md:flex-row gap-3">
          <Input
            value={inputAlertId}
            onChange={(e) => setInputAlertId(e.target.value)}
            placeholder="Enter Alert ID (e.g., ALT-1000)"
            className="bg-input border-border"
          />
          <Button onClick={() => setActiveAlertId(inputAlertId.trim())}>Load Investigation</Button>
        </CardContent>
      </Card>

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
                <p className="font-semibold text-foreground">{activeAlertId}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Entity</p>
                <p className="font-semibold text-foreground">{investigation?.entity || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <p className="font-semibold text-foreground">{investigation?.status || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-2">Risk Score</p>
                <div className="flex items-end gap-2">
                  <Progress value={Math.min(investigation?.risk_score || 0, 100)} className="flex-1" />
                  <span className="font-bold text-accent text-lg">{(investigation?.risk_score || 0).toFixed(1)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <Card className="bg-card border-border">
            <CardContent className="pt-6 space-y-2">
              <Button
                className="w-full bg-accent hover:bg-accent/90 text-foreground"
                onClick={() => decisionMutation.mutate('FRAUD')}
                disabled={decisionMutation.isPending || isLoading}
              >
                Mark as Fraud
              </Button>
              <Button
                variant="outline"
                className="w-full border-border bg-transparent"
                onClick={() => decisionMutation.mutate('LEGITIMATE')}
                disabled={decisionMutation.isPending || isLoading}
              >
                Mark as Legitimate
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
                {transactionDetails.map((item: { label: string; value: string }) => (
                  <div key={item.label}>
                    <p className="text-xs text-muted-foreground uppercase">{item.label}</p>
                    <p className="font-mono text-sm text-foreground">{item.value}</p>
                  </div>
                ))}
                {!isLoading && transactionDetails.length === 0 && (
                  <p className="text-sm text-muted-foreground">No transaction context found.</p>
                )}
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
                {(investigation?.feature_deviations || []).map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-secondary/30 rounded-lg">
                    <div>
                      <p className="font-medium text-foreground text-sm">{item.feature}</p>
                      <p className="text-xs text-muted-foreground">{item.deviation}</p>
                    </div>
                    <span className={`text-xs font-semibold px-2 py-1 rounded ${riskPillClass(item.risk_level)}`}>
                      {item.risk_level.replace('_', ' ')}
                    </span>
                  </div>
                ))}
                {!isLoading && (investigation?.feature_deviations || []).length === 0 && (
                  <p className="text-sm text-muted-foreground">No feature deviations recorded.</p>
                )}
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
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          <Button
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
            onClick={() => noteMutation.mutate()}
            disabled={!note.trim() || noteMutation.isPending || isLoading}
          >
            Add Note
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
