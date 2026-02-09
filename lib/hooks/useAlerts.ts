'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertsService } from '../services/alerts.service'
import { Alert, AlertDetail, AlertFilters, AlertsResponse, InvestigationDecision } from '../types'

const ALERTS_KEY = 'alerts'
const ALERT_DETAIL_KEY = 'alert-detail'

export function useAlerts(filters: AlertFilters = {}) {
  return useQuery({
    queryKey: [ALERTS_KEY, filters],
    queryFn: () => AlertsService.getAlerts(filters),
    staleTime: 30 * 1000, // 30 seconds
    retry: 2,
  })
}

export function useAlertDetail(alert_id: string) {
  return useQuery({
    queryKey: [ALERT_DETAIL_KEY, alert_id],
    queryFn: () => AlertsService.getAlertDetail(alert_id),
    enabled: !!alert_id,
    staleTime: 60 * 1000, // 1 minute
    retry: 2,
  })
}

export function useSubmitDecision() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ alert_id, decision }: { alert_id: string; decision: InvestigationDecision }) =>
      AlertsService.submitDecision(alert_id, decision),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ALERTS_KEY] })
      queryClient.invalidateQueries({ queryKey: [ALERT_DETAIL_KEY] })
    },
  })
}

export function useSearchAlerts(query: string) {
  return useQuery({
    queryKey: [ALERTS_KEY, 'search', query],
    queryFn: () => AlertsService.searchAlerts(query),
    enabled: query.length > 0,
    staleTime: 20 * 1000,
  })
}
