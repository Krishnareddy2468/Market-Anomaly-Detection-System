export type AlertSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
export type AlertStatus = 'ACTIVE' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE'

export interface Alert {
  alert_id: string
  timestamp: string
  entity: string
  risk_score: number
  severity: AlertSeverity
  status: AlertStatus
}

export interface AlertDetail {
  alert_id: string
  timestamp: string
  entity: string
  status: AlertStatus
  risk_score: number
  severity: AlertSeverity
  description?: string
  transaction?: Transaction
  feature_deviations: FeatureDeviation[]
  historical_scores?: number[]
}

export interface Transaction {
  transaction_id: string
  amount: number
  currency: string
  timestamp: string
  source_account: string
  destination_account: string
  channel?: string
  ip_address?: string
  device_fingerprint?: string
}

export interface FeatureDeviation {
  feature: string
  deviation: string
  risk_level: 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW' | 'MINIMAL'
  value?: number
  baseline?: number
}

export interface AlertsResponse {
  data: Alert[]
  pagination: {
    page: number
    total_pages: number
    total_records: number
  }
}

export interface AlertFilters {
  page?: number
  limit?: number
  severity?: AlertSeverity | 'ALL'
  status?: AlertStatus | 'ALL'
  search?: string
}

export interface InvestigationDecision {
  decision: 'FRAUD' | 'LEGITIMATE' | 'REVIEW'
  notes?: string
  analyst_id?: string
}

export interface InvestigationResponse {
  success: boolean
  alert_id: string
  updated_status: AlertStatus
  message: string
}

export interface InvestigationNote {
  note_id: string
  content: string
  analyst_id: string
  timestamp: string
}

export interface Investigation {
  alert_id: string
  entity: string
  status: AlertStatus
  risk_score: number
  transaction?: Transaction
  feature_deviations: FeatureDeviation[]
  historical_behavior: Array<{ date: string; score: number; model?: string }>
  notes: InvestigationNote[]
}
