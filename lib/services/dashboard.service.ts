import { AlertsTrend, DashboardMetrics } from '../types'
import { ApiClient } from './api-client'

export class DashboardService {
  static async getMetrics(): Promise<DashboardMetrics> {
    try {
      const response = await ApiClient.get<{ data: DashboardMetrics }>('/api/dashboard/metrics')
      return response.data
    } catch (error) {
      console.error('[v0] Failed to fetch dashboard metrics:', error)
      throw error
    }
  }

  static async getAlertsTrend(range: string = '24h'): Promise<AlertsTrend> {
    try {
      const response = await ApiClient.get<{ data: AlertsTrend }>(`/api/dashboard/alerts-trend?range=${range}`)
      return response.data
    } catch (error) {
      console.error('[v0] Failed to fetch alerts trend:', error)
      throw error
    }
  }

  static async getSeverityDistribution() {
    try {
      const response = await ApiClient.get<{ data: any }>('/api/dashboard/severity-distribution')
      return response.data
    } catch (error) {
      console.error('[v0] Failed to fetch severity distribution:', error)
      throw error
    }
  }

  static async getDashboardData(): Promise<{
    metrics: DashboardMetrics
    trend: AlertsTrend
  }> {
    const [metrics, trend] = await Promise.all([this.getMetrics(), this.getAlertsTrend()])

    return { metrics, trend }
  }
}
