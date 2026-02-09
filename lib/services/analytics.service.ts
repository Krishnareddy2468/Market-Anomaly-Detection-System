import { AnalyticsMetrics, FeedbackItem } from '../types'
import { ApiClient } from './api-client'

export class AnalyticsService {
  static async getPerformanceMetrics(): Promise<AnalyticsMetrics> {
    const response = await ApiClient.get<{ data: AnalyticsMetrics }>('/api/analytics/metrics')
    return response.data
  }

  static async getAnalyticsTrends() {
    const response = await ApiClient.get<{ data: any[] }>('/api/analytics/trends')
    return response.data
  }

  static async getFeedbackHistory(page: number = 1, limit: number = 20): Promise<{
    data: FeedbackItem[]
    pagination: { page: number; total_pages: number; total_records: number }
  }> {
    return ApiClient.get(`/api/feedback?page=${page}&limit=${limit}`)
  }

  static async getSystemHealth(): Promise<{
    uptime: number
    last_sync: string
    model_version: string
  }> {
    return ApiClient.get('/api/analytics/health')
  }
}
