'use client'

import { PageContainer } from '@/components/layout/page-container'
import { LiveScannerCard } from '@/components/cards/live-scanner-card'

export function ScannerPage() {
  return (
    <PageContainer>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold text-foreground tracking-tight">Live Scanner</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Run a transaction through the detection engine and see its risk score in real time
          </p>
        </div>

        <LiveScannerCard />
      </div>
    </PageContainer>
  )
}
