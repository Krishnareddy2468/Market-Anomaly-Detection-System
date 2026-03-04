'use client'

import { useQuery } from '@tanstack/react-query'
import { AnalyticsService } from '../services/analytics.service'

const ANALYTICS_KEY = 'analytics'

export function usePerformanceMetrics() {
  return useQuery({
    queryKey: [ANALYTICS_KEY, 'performance'],
    queryFn: () => AnalyticsService.getPerformanceMetrics(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  })
}

export function useFeedbackHistory(page: number = 1, limit: number = 20) {
  return useQuery({
    queryKey: [ANALYTICS_KEY, 'feedback', page, limit],
    queryFn: () => AnalyticsService.getFeedbackHistory(page, limit),
    staleTime: 60 * 1000,
    retry: 2,
  })
}

export function useAnalyticsTrends() {
  return useQuery({
    queryKey: [ANALYTICS_KEY, 'trends'],
    queryFn: () => AnalyticsService.getAlertVolume('7d', 'day'),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  })
}

export function useModelPerformance() {
  return useQuery({
    queryKey: [ANALYTICS_KEY, 'model-performance'],
    queryFn: () => AnalyticsService.getModelPerformance('7d'),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  })
}

export function useConfusionMatrix() {
  return useQuery({
    queryKey: [ANALYTICS_KEY, 'confusion-matrix'],
    queryFn: () => AnalyticsService.getConfusionMatrix(),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  })
}

export function useDetectionRate() {
  return useQuery({
    queryKey: [ANALYTICS_KEY, 'detection-rate'],
    queryFn: () => AnalyticsService.getDetectionRate('7d'),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  })
}

export function useSystemHealth() {
  return useQuery({
    queryKey: [ANALYTICS_KEY, 'health'],
    queryFn: () => AnalyticsService.getSystemHealth(),
    staleTime: 30 * 1000,
    retry: 1,
  })
}
