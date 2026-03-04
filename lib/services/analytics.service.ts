import { AlertVolume, AnalyticsMetrics, ConfusionMatrix, DetectionRate, FeedbackItem, ModelPerformance } from '../types'
import { ApiClient } from './api-client'

export class AnalyticsService {
  static async getPerformanceMetrics(): Promise<AnalyticsMetrics> {
    const response = await ApiClient.get<{ data: AnalyticsMetrics }>('/api/analytics/metrics')
    return response.data
  }

  static async getAlertVolume(range: '7d' | '30d' | '90d' = '7d', groupBy: 'day' | 'hour' = 'day'): Promise<AlertVolume> {
    const response = await ApiClient.get<{ data: AlertVolume }>(
      `/api/analytics/alert-volume?range=${range}&group_by=${groupBy}`,
    )
    return response.data
  }

  static async getModelPerformance(range: '7d' | '30d' | '90d' = '7d'): Promise<ModelPerformance> {
    const response = await ApiClient.get<{ data: ModelPerformance }>(
      `/api/analytics/model-performance?range=${range}`,
    )
    return response.data
  }

  static async getConfusionMatrix(): Promise<ConfusionMatrix> {
    const response = await ApiClient.get<{ data: ConfusionMatrix }>('/api/analytics/confusion-matrix')
    return response.data
  }

  static async getDetectionRate(range: '7d' | '30d' | '90d' = '7d'): Promise<DetectionRate> {
    const response = await ApiClient.get<{ data: DetectionRate }>(`/api/analytics/detection-rate?range=${range}`)
    return response.data
  }

  static async getFeedbackHistory(page: number = 1, limit: number = 20): Promise<{
    data: FeedbackItem[]
    pagination: { page: number; total_pages: number; total_records: number }
    summary?: { total_resolutions: number; confirmed_frauds: number; false_positives: number; resolution_rate: number }
  }> {
    return ApiClient.get(`/api/feedback?page=${page}&limit=${limit}`)
  }

  static async getSystemHealth(): Promise<{ status: string; app: string; version: string; environment: string }> {
    return ApiClient.get('/health')
  }
}
