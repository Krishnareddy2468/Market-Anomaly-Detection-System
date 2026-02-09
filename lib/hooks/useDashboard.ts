'use client'

import { useQuery } from '@tanstack/react-query'
import { DashboardService } from '../services/dashboard.service'

const DASHBOARD_KEY = 'dashboard'

export function useDashboardMetrics() {
  return useQuery({
    queryKey: [DASHBOARD_KEY, 'metrics'],
    queryFn: () => DashboardService.getMetrics(),
    staleTime: 60 * 1000, // 1 minute
    retry: 2,
  })
}

export function useAlertsTrend(range: string = '24h') {
  return useQuery({
    queryKey: [DASHBOARD_KEY, 'trend', range],
    queryFn: () => DashboardService.getAlertsTrend(range),
    staleTime: 60 * 1000,
    retry: 2,
  })
}

export function useDashboardData(range: string = '24h') {
  const metrics = useDashboardMetrics()
  const trend = useAlertsTrend(range)

  return {
    metrics: metrics.data,
    trend: trend.data,
    isLoading: metrics.isLoading || trend.isLoading,
    error: metrics.error || trend.error,
    isFetching: metrics.isFetching || trend.isFetching,
  }
}
