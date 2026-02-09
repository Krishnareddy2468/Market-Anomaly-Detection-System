'use client'

import { useState } from 'react'
import { useAlerts } from '@/lib/hooks/useAlerts'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { AlertsDataTable } from '@/components/tables/alerts-data-table'
import { PageContainer } from '@/components/layout/page-container'
import { Search, Filter } from 'lucide-react'
import { AlertSeverity, AlertStatus } from '@/lib/types'
import { ALERT_SEVERITY_OPTIONS, ALERT_STATUS_OPTIONS } from '@/lib/utils/constants'

export function AlertsPage() {
  const [page, setPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [severity, setSeverity] = useState<AlertSeverity | 'ALL'>('ALL')
  const [status, setStatus] = useState<AlertStatus | 'ALL'>('ALL')

  const { data: alertsData, isLoading } = useAlerts({
    page,
    limit: 10,
    severity: severity as any,
    status: status as any,
    search: searchTerm || undefined,
  })

  const handleRowClick = (alert: any) => {
    console.log('[v0] Alert selected:', alert.alert_id)
  }

  return (
    <PageContainer>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Alerts</h1>
          <p className="text-muted-foreground mt-1">Active fraud detection alerts and anomalies</p>
        </div>

        {/* Filters */}
        <Card className="p-6 bg-card border-border">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-lg font-semibold text-foreground">Filters</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search Alert ID or Entity..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value)
                  setPage(1)
                }}
                className="pl-10 bg-input border-border"
              />
            </div>

            {/* Severity Filter */}
            <Select value={severity} onValueChange={(value) => {
              setSeverity(value as AlertSeverity | 'ALL')
              setPage(1)
            }}>
              <SelectTrigger className="bg-input border-border">
                <SelectValue placeholder="Filter by Severity" />
              </SelectTrigger>
              <SelectContent>
                {ALERT_SEVERITY_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Status Filter */}
            <Select value={status} onValueChange={(value) => {
              setStatus(value as AlertStatus | 'ALL')
              setPage(1)
            }}>
              <SelectTrigger className="bg-input border-border">
                <SelectValue placeholder="Filter by Status" />
              </SelectTrigger>
              <SelectContent>
                {ALERT_STATUS_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </Card>

        {/* Alerts Table */}
        <Card className="p-6 bg-card border-border">
          <h3 className="text-lg font-semibold mb-4 text-foreground">
            Alerts {alertsData?.pagination && `(${alertsData.pagination.total_records})`}
          </h3>
          <AlertsDataTable
            data={alertsData?.data || []}
            isLoading={isLoading}
            onRowClick={handleRowClick}
          />
        </Card>
      </div>
    </PageContainer>
  )
}
