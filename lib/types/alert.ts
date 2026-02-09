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
  entity: string
  status: AlertStatus
  risk_score: number
  transaction: Transaction
  feature_deviations: FeatureDeviation[]
}

export interface Transaction {
  transaction_id: string
  amount: number
  currency: string
  timestamp: string
  source_account: string
  destination_account: string
  ip_address: string
}

export interface FeatureDeviation {
  feature: string
  deviation: string
  severity: AlertSeverity
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
  notes: string
}

export interface InvestigationResponse {
  status: 'SUCCESS' | 'ERROR'
  updated_alert_status: AlertStatus
}
