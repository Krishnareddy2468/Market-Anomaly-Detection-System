'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Input } from '@/components/ui/input'
import { Zap, AlertTriangle, CheckCircle, Loader2, PenLine } from 'lucide-react'

const CHANNELS = ['WEB', 'POS', 'API', 'MOBILE', 'ATM'] as const

/** Build an ISO-8601 string that preserves the intended hour (no UTC shift). */
function localISOTimestamp(hour: number, minute = 17): string {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(hour).padStart(2, '0')
  const min = String(minute).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}T${hh}:${min}:00`
}

const DEMO_SCENARIOS = [
  {
    label: 'Suspicious: ₹76.7L at 2 AM, unknown IP',
    payload: {
      transaction_id: `LIVE-${Date.now()}`,
      amount: 76_70_000,
      timestamp: localISOTimestamp(2),
      source_account: 'ACC-8042',
      destination_account: 'ACC-9999',
      entity_id: 'ENT-SCAN-SUS',
      entity_type: 'USER',
      currency: 'INR',
      channel: 'API',
      ip_address: '185.220.101.45',
      geo_country: 'XX',
      historical_transactions: [
        { transaction_id: 'H1', amount: 20_350, timestamp: new Date(Date.now() - 2 * 86400000).toISOString(), destination_account: 'ACC-9100', channel: 'WEB' },
        { transaction_id: 'H2', amount: 25_700, timestamp: new Date(Date.now() - 4 * 86400000).toISOString(), destination_account: 'ACC-9101', channel: 'WEB' },
        { transaction_id: 'H3', amount: 23_240, timestamp: new Date(Date.now() - 6 * 86400000).toISOString(), destination_account: 'ACC-9102', channel: 'WEB' },
        { transaction_id: 'H4', amount: 16_185, timestamp: new Date(Date.now() - 8 * 86400000).toISOString(), destination_account: 'ACC-9103', channel: 'WEB' },
        { transaction_id: 'H5', amount: 21_580, timestamp: new Date(Date.now() - 10 * 86400000).toISOString(), destination_account: 'ACC-9104', channel: 'WEB' },
      ],
    },
  },
  {
    label: 'Normal: ₹2,850 grocery purchase',
    payload: {
      transaction_id: `LIVE-${Date.now()}`,
      amount: 2_850,
      timestamp: new Date().toISOString(),
      source_account: 'ACC-8200',
      destination_account: 'ACC-9050',
      entity_id: 'ENT-SCAN-NORM',
      entity_type: 'USER',
      currency: 'INR',
      channel: 'POS',
      ip_address: '192.168.1.40',
      geo_country: 'IN',
      historical_transactions: [
        { transaction_id: 'H1', amount: 2_700, timestamp: new Date(Date.now() - 7 * 86400000).toISOString(), destination_account: 'ACC-9050', channel: 'POS' },
        { transaction_id: 'H2', amount: 3_400, timestamp: new Date(Date.now() - 14 * 86400000).toISOString(), destination_account: 'ACC-9050', channel: 'POS' },
        { transaction_id: 'H3', amount: 2_400, timestamp: new Date(Date.now() - 21 * 86400000).toISOString(), destination_account: 'ACC-9050', channel: 'POS' },
        { transaction_id: 'H4', amount: 2_990, timestamp: new Date(Date.now() - 28 * 86400000).toISOString(), destination_account: 'ACC-9050', channel: 'POS' },
        { transaction_id: 'H5', amount: 3_150, timestamp: new Date(Date.now() - 35 * 86400000).toISOString(), destination_account: 'ACC-9050', channel: 'POS' },
      ],
    },
  },
  {
    label: 'Velocity spike: 6 rapid ₹15L wire transfers',
    payload: {
      transaction_id: `LIVE-${Date.now()}`,
      amount: 15_10_000,
      timestamp: new Date().toISOString(),
      source_account: 'ACC-8077',
      destination_account: 'ACC-9331',
      entity_id: 'ENT-SCAN-VEL',
      entity_type: 'ACCOUNT',
      currency: 'INR',
      channel: 'API',
      ip_address: '203.0.113.77',
      geo_country: 'DE',
      historical_transactions: [
        { transaction_id: 'V1', amount: 14_52_500, timestamp: new Date(Date.now() - 8 * 60000).toISOString(), destination_account: 'ACC-9332', channel: 'API' },
        { transaction_id: 'V2', amount: 13_94_400, timestamp: new Date(Date.now() - 16 * 60000).toISOString(), destination_account: 'ACC-9333', channel: 'API' },
        { transaction_id: 'V3', amount: 15_68_700, timestamp: new Date(Date.now() - 24 * 60000).toISOString(), destination_account: 'ACC-9334', channel: 'API' },
        { transaction_id: 'V4', amount: 14_19_300, timestamp: new Date(Date.now() - 32 * 60000).toISOString(), destination_account: 'ACC-9335', channel: 'API' },
        { transaction_id: 'V5', amount: 16_01_900, timestamp: new Date(Date.now() - 40 * 60000).toISOString(), destination_account: 'ACC-9336', channel: 'API' },
        { transaction_id: 'H1', amount: 23_240, timestamp: new Date(Date.now() - 3 * 86400000).toISOString(), destination_account: 'ACC-9050', channel: 'WEB' },
        { transaction_id: 'H2', amount: 25_730, timestamp: new Date(Date.now() - 6 * 86400000).toISOString(), destination_account: 'ACC-9050', channel: 'WEB' },
      ],
    },
  },
]

interface DetectionResult {
  risk_score: number
  severity: string
  should_alert: boolean
  detector_scores: Record<string, number>
  explanations: string[]
  processing_time_ms: number
}

const severityColor: Record<string, string> = {
  CRITICAL: 'bg-red-500',
  HIGH: 'bg-orange-500',
  MEDIUM: 'bg-yellow-500',
  LOW: 'bg-green-500',
}

const severityBadgeVariant: Record<string, 'destructive' | 'default' | 'secondary' | 'outline'> = {
  CRITICAL: 'destructive',
  HIGH: 'destructive',
  MEDIUM: 'secondary',
  LOW: 'outline',
}

export function LiveScannerCard() {
  const [selectedIdx, setSelectedIdx] = useState(0)
  const [customMode, setCustomMode] = useState(false)
  const [customAmount, setCustomAmount] = useState('')
  const [customChannel, setCustomChannel] = useState<string>('API')
  const [customHour, setCustomHour] = useState('2')
  const [result, setResult] = useState<DetectionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const buildCustomPayload = () => {
    const amount = parseFloat(customAmount) || 0
    const hour = parseInt(customHour) || 0
    const stamp = Date.now()
    return {
      transaction_id: `CUSTOM-${stamp}`,
      amount,
      timestamp: localISOTimestamp(hour),
      source_account: 'ACC-CUSTOM-01',
      destination_account: 'ACC-CUSTOM-99',
      entity_id: `ENT-CUSTOM-${stamp}`,
      entity_type: 'USER',
      currency: 'INR',
      channel: customChannel,
      ip_address: '203.0.113.42',
      geo_country: 'IN',
      historical_transactions: [
        { transaction_id: 'H1', amount: 18_500, timestamp: new Date(Date.now() - 2 * 86400000).toISOString(), destination_account: 'ACC-9100', channel: 'WEB' },
        { transaction_id: 'H2', amount: 22_300, timestamp: new Date(Date.now() - 5 * 86400000).toISOString(), destination_account: 'ACC-9100', channel: 'WEB' },
        { transaction_id: 'H3', amount: 15_800, timestamp: new Date(Date.now() - 9 * 86400000).toISOString(), destination_account: 'ACC-9100', channel: 'WEB' },
        { transaction_id: 'H4', amount: 20_100, timestamp: new Date(Date.now() - 13 * 86400000).toISOString(), destination_account: 'ACC-9100', channel: 'WEB' },
        { transaction_id: 'H5', amount: 17_600, timestamp: new Date(Date.now() - 17 * 86400000).toISOString(), destination_account: 'ACC-9100', channel: 'WEB' },
      ],
    }
  }

  const handleScan = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    let payload: Record<string, unknown>

    if (customMode) {
      if (!customAmount || parseFloat(customAmount) <= 0) {
        setError('Enter a valid amount in ₹')
        setLoading(false)
        return
      }
      payload = buildCustomPayload()
    } else {
      const scenario = DEMO_SCENARIOS[selectedIdx]
      payload = {
        ...scenario.payload,
        transaction_id: `LIVE-${Date.now()}`,
        entity_id: `${scenario.payload.entity_id}-${Date.now()}`,
      }
    }

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || ''
      const res = await fetch(`${apiBase}/api/detection/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error(`API returned ${res.status}`)
      const json = await res.json()
      setResult(json.data)
    } catch (err) {
      setError('Detection service unavailable. Start the backend to run live scans.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="bg-card border-border overflow-hidden">
      {/* Header with gradient accent */}
      <div className="relative">
        <div className="absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500" />
        <CardHeader className="pb-3 pt-5">
          <CardTitle className="flex items-center gap-2.5 text-foreground text-base">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10">
              <Zap className="h-4 w-4 text-amber-500" />
            </div>
            <div>
              <span className="font-semibold">Live Transaction Scanner</span>
              <p className="text-[10px] font-normal text-muted-foreground mt-0.5">Isolation Forest + Behavioral + Statistical</p>
            </div>
            <div className="ml-auto flex items-center gap-1.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <span className="text-[10px] font-medium text-emerald-500 uppercase tracking-wider">Live</span>
            </div>
          </CardTitle>
        </CardHeader>
      </div>
      <CardContent className="space-y-4">
        {/* Mode Toggle */}
        <div className="flex items-center gap-2">
          <Button
            variant={customMode ? 'outline' : 'default'}
            size="sm"
            onClick={() => { setCustomMode(false); setResult(null); setError(null) }}
          >
            Preset Scenarios
          </Button>
          <Button
            variant={customMode ? 'default' : 'outline'}
            size="sm"
            onClick={() => { setCustomMode(true); setResult(null); setError(null) }}
          >
            <PenLine className="h-3.5 w-3.5 mr-1.5" />
            Custom Transaction
          </Button>
        </div>

        {/* Scenario Selector OR Custom Inputs */}
        {!customMode ? (
          <div className="flex flex-col sm:flex-row gap-3">
            <select
              className="flex-1 rounded-md border border-border bg-input text-foreground text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-primary"
              value={selectedIdx}
              onChange={(e) => {
                setSelectedIdx(Number(e.target.value))
                setResult(null)
                setError(null)
              }}
            >
              {DEMO_SCENARIOS.map((s, i) => (
                <option key={i} value={i}>{s.label}</option>
              ))}
            </select>
            <Button
              onClick={handleScan}
              disabled={loading}
              className="bg-primary hover:bg-primary/90 text-primary-foreground shrink-0"
            >
              {loading ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Scanning…</>
              ) : (
                <><Zap className="h-4 w-4 mr-2" />Scan Now</>
              )}
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Amount (₹)</label>
                <Input
                  type="number"
                  placeholder="e.g. 5000000"
                  value={customAmount}
                  onChange={(e) => { setCustomAmount(e.target.value); setResult(null) }}
                  className="bg-input"
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Channel</label>
                <select
                  className="w-full rounded-md border border-border bg-input text-foreground text-sm px-3 py-2 focus:outline-none focus:ring-1 focus:ring-primary h-9"
                  value={customChannel}
                  onChange={(e) => { setCustomChannel(e.target.value); setResult(null) }}
                >
                  {CHANNELS.map((ch) => (
                    <option key={ch} value={ch}>{ch}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Hour (0–23)</label>
                <Input
                  type="number"
                  min={0}
                  max={23}
                  placeholder="2"
                  value={customHour}
                  onChange={(e) => { setCustomHour(e.target.value); setResult(null) }}
                  className="bg-input"
                />
              </div>
            </div>
            {customAmount && (
              <p className="text-xs text-muted-foreground">
                Scoring: <span className="font-medium text-foreground">₹{Number(customAmount).toLocaleString('en-IN')}</span> via {customChannel} at {customHour}:00
              </p>
            )}
            <Button
              onClick={handleScan}
              disabled={loading}
              className="bg-primary hover:bg-primary/90 text-primary-foreground w-full sm:w-auto"
            >
              {loading ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Scanning…</>
              ) : (
                <><Zap className="h-4 w-4 mr-2" />Scan Now</>
              )}
            </Button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="text-sm text-destructive bg-destructive/10 rounded p-3">{error}</div>
        )}

        {/* Result */}
        {result && (
          <div className="space-y-4 pt-2">
            {/* Score Hero */}
            <div className="rounded-xl border border-border bg-muted/30 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Risk Score</span>
                <div className="flex items-center gap-2">
                  <Badge variant={severityBadgeVariant[result.severity] ?? 'secondary'} className="text-[10px] px-2 py-0.5">
                    {result.severity}
                  </Badge>
                  <span className="text-xs text-muted-foreground">{result.processing_time_ms.toFixed(0)} ms</span>
                </div>
              </div>
              <div className="flex items-end gap-3">
                <span className="text-4xl font-bold tracking-tight text-foreground">{result.risk_score.toFixed(1)}</span>
                <span className="text-sm text-muted-foreground mb-1">/ 100</span>
              </div>
              <div className="relative h-2 rounded-full bg-muted overflow-hidden">
                <div
                  className={`absolute inset-y-0 left-0 rounded-full transition-all duration-700 ease-out ${
                    result.severity === 'CRITICAL' ? 'bg-red-500' :
                    result.severity === 'HIGH' ? 'bg-orange-500' :
                    result.severity === 'MEDIUM' ? 'bg-yellow-500' :
                    'bg-emerald-500'
                  }`}
                  style={{ width: `${result.risk_score}%` }}
                />
              </div>
            </div>

            {/* Detector breakdown */}
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(result.detector_scores).map(([model, score]) => {
                const s = Number(score)
                const barColor = s >= 70 ? 'bg-red-500' : s >= 40 ? 'bg-yellow-500' : 'bg-emerald-500'
                return (
                  <div key={model} className="rounded-lg border border-border bg-card p-3 space-y-2">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wide capitalize">{model.replace('_', ' ')}</div>
                    <div className="text-lg font-bold text-foreground">{s.toFixed(1)}</div>
                    <div className="h-1 rounded-full bg-muted overflow-hidden">
                      <div className={`h-full rounded-full ${barColor} transition-all duration-500`} style={{ width: `${s}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Alert decision */}
            <div className={`flex items-center gap-2 text-sm rounded-lg px-3 py-2.5 ${
              result.should_alert
                ? 'bg-red-500/10 border border-red-500/20'
                : 'bg-emerald-500/10 border border-emerald-500/20'
            }`}>
              {result.should_alert ? (
                <><AlertTriangle className="h-4 w-4 text-red-500" /><span className="text-red-500 font-medium">Alert Generated</span></>
              ) : (
                <><CheckCircle className="h-4 w-4 text-emerald-500" /><span className="text-emerald-500 font-medium">No Alert Required</span></>
              )}
            </div>

            {/* Explanations */}
            {result.explanations.length > 0 && (
              <div className="space-y-2">
                <p className="text-[10px] text-muted-foreground font-semibold uppercase tracking-widest">Detection Signals</p>
                <div className="grid gap-1.5">
                  {result.explanations.map((exp, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-foreground">
                      <span className="mt-1 h-1 w-1 rounded-full bg-primary shrink-0" />
                      <span>{exp}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
