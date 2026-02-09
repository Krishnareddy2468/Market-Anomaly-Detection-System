export interface DashboardMetrics {
  total_transactions: number
  active_alerts: number
  high_risk_alerts: number
  false_positive_rate: number
  trends: {
    alerts_change_pct: number
    false_positive_change_pct: number
  }
}

export interface AlertsTrendPoint {
  timestamp: string
  value: number
}

export interface AlertsTrend {
  timestamps: string[]
  values: number[]
}

export interface AnalyticsMetrics {
  precision: number
  recall: number
  f1_score: number
  alert_volume_daily: number
}

export interface FeedbackItem {
  feedback_id: string
  alert_id: string
  entity: string
  decision: string
  notes: string
  resolved_at: string
  analyst: string
}
