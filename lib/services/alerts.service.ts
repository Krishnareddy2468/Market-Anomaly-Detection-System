import { Alert, AlertDetail, AlertFilters, AlertsResponse, Investigation, InvestigationDecision, InvestigationResponse } from '../types'
import { ApiClient } from './api-client'

export class AlertsService {
  static async getAlerts(filters: AlertFilters): Promise<AlertsResponse> {
    const params = new URLSearchParams()

    if (filters.page) params.append('page', String(filters.page))
    if (filters.limit) params.append('limit', String(filters.limit))
    if (filters.severity && filters.severity !== 'ALL') params.append('severity', filters.severity)
    if (filters.status && filters.status !== 'ALL') params.append('status', filters.status)
    if (filters.search) params.append('search', filters.search)

    const query = params.toString()
    const endpoint = `/api/alerts${query ? `?${query}` : ''}`

    try {
      return await ApiClient.get<AlertsResponse>(endpoint)
    } catch (error) {
      console.error('[v0] Failed to fetch alerts:', error)
      throw error
    }
  }

  static async getAlertDetail(alert_id: string): Promise<AlertDetail> {
    const response = await ApiClient.get<{ data: AlertDetail }>(`/api/alerts/${alert_id}`)
    return response.data
  }

  static async submitDecision(
    alert_id: string,
    decision: InvestigationDecision,
  ): Promise<InvestigationResponse> {
    return ApiClient.post<InvestigationResponse>(`/api/investigations/${alert_id}/decision`, decision)
  }

  static async getInvestigation(alert_id: string): Promise<Investigation> {
    const response = await ApiClient.get<{ data: Investigation }>(`/api/investigations/${alert_id}`)
    return response.data
  }

  static async addInvestigationNote(
    alert_id: string,
    content: string,
    analyst_id: string = 'system',
  ): Promise<void> {
    await ApiClient.post(`/api/investigations/${alert_id}/notes`, { content, analyst_id })
  }

  static async updateAlertStatus(alert_id: string, status: string): Promise<void> {
    await ApiClient.patch(`/api/alerts/${alert_id}/status?status=${encodeURIComponent(status)}`)
  }

  static async searchAlerts(query: string): Promise<Alert[]> {
    const response = await this.getAlerts({ search: query, limit: 20 })
    return response.data
  }
}
