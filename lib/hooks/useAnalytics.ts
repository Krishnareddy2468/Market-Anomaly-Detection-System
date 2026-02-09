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
    queryFn: () => AnalyticsService.getAnalyticsTrends(),
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
