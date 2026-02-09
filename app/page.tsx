'use client'

import { useState, Suspense } from 'react'
import { Sidebar } from '@/components/sidebar'
import { TopBar } from '@/components/top-bar'
import { Dashboard } from '@/components/pages/dashboard'
import { AlertsPage } from '@/components/pages/alerts'
import { InvestigationPage } from '@/components/pages/investigation'
import { AnalyticsPage } from '@/components/pages/analytics'
import { FeedbackPage } from '@/components/pages/feedback'
import { SettingsPage } from '@/components/pages/settings'

type Page = 'dashboard' | 'alerts' | 'investigations' | 'analytics' | 'feedback' | 'settings'

const LoadingPlaceholder = () => (
  <div className="p-6 text-center text-muted-foreground">
    <p>Loading page...</p>
  </div>
)

export default function Home() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const renderPage = () => {
    switch (currentPage) {
      case 'alerts':
        return <AlertsPage />
      case 'investigations':
        return <InvestigationPage />
      case 'analytics':
        return <AnalyticsPage />
      case 'feedback':
        return <FeedbackPage />
      case 'settings':
        return <SettingsPage />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="h-screen bg-background text-foreground flex flex-col">
      <Sidebar
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      <div className="flex-1 flex flex-col overflow-hidden" style={{ marginLeft: sidebarOpen ? '16rem' : '5rem' }}>
        <TopBar
          pageTitle={
            {
              dashboard: 'Dashboard',
              alerts: 'Alerts',
              investigations: 'Investigations',
              analytics: 'Analytics',
              feedback: 'Feedback History',
              settings: 'Settings',
            }[currentPage]
          }
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
        />
        <main className="flex-1 overflow-auto bg-background">
          <Suspense fallback={<LoadingPlaceholder />}>
            {renderPage()}
          </Suspense>
        </main>
      </div>
    </div>
  )
}
