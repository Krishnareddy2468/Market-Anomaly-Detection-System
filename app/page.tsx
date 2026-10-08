'use client'

import { useState, Suspense } from 'react'
import { Sidebar } from '@/components/sidebar'
import { TopBar } from '@/components/top-bar'
import { Dashboard } from '@/components/pages/dashboard'
import { ScannerPage } from '@/components/pages/scanner'
import { AlertsPage } from '@/components/pages/alerts'
import { InvestigationPage } from '@/components/pages/investigation'
import { AnalyticsPage } from '@/components/pages/analytics'
import { FeedbackPage } from '@/components/pages/feedback'
import { SettingsPage } from '@/components/pages/settings'
import { AboutPage } from '@/components/pages/about'
import { CurrencyProvider } from '@/lib/contexts/currency-context'

type Page = 'dashboard' | 'scanner' | 'alerts' | 'investigations' | 'analytics' | 'feedback' | 'settings' | 'about'

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
      case 'scanner':
        return <ScannerPage />
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
      case 'about':
        return <AboutPage />
      default:
        return <Dashboard />
    }
  }

  return (
    <CurrencyProvider>
      <div className="h-screen bg-background text-foreground flex flex-col">
        <Sidebar
          currentPage={currentPage}
          onPageChange={setCurrentPage}
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
        />
        <div className="flex-1 flex flex-col overflow-hidden transition-all duration-300 ease-in-out" style={{ marginLeft: sidebarOpen ? '16rem' : '4.5rem' }}>
          <TopBar
            pageTitle={
              {
                dashboard: 'Dashboard',
                scanner: 'Live Scanner',
                alerts: 'Alerts',
                investigations: 'Investigations',
                analytics: 'Analytics',
                feedback: 'Feedback History',
                settings: 'Settings',
                about: 'About',
              }[currentPage]
            }
            onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
          />
          <main className="flex-1 overflow-auto bg-background">
            <Suspense fallback={<LoadingPlaceholder />}>
              {renderPage()}
            </Suspense>
          </main>
          <footer className="border-t border-border bg-card/60 px-6 py-2.5 text-center">
            <p className="text-xs text-muted-foreground">
              Demo environment · For a full demo, contact{' '}
              <a
                href="mailto:nkrishnareddy2003@gmail.com"
                className="font-medium text-primary hover:underline"
              >
                nkrishnareddy2003@gmail.com
              </a>
            </p>
          </footer>
        </div>
      </div>
    </CurrencyProvider>
  )
}
