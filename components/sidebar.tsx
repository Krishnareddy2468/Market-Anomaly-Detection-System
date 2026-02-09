'use client';

import { ChevronLeft, ChevronRight, LayoutDashboard, AlertCircle, Search, TrendingUp, History, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface SidebarProps {
  currentPage: string
  onPageChange: (page: any) => void
  isOpen: boolean
  onToggle: () => void
}

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'alerts', label: 'Alerts', icon: AlertCircle },
  { id: 'investigations', label: 'Investigations', icon: Search },
  { id: 'analytics', label: 'Analytics', icon: TrendingUp },
  { id: 'feedback', label: 'Feedback History', icon: History },
  { id: 'settings', label: 'Settings', icon: Settings },
]

export function Sidebar({ currentPage, onPageChange, isOpen, onToggle }: SidebarProps) {
  return (
    <div
      className={`fixed left-0 top-0 bottom-0 bg-primary text-sidebar-foreground transition-all duration-300 z-40 flex flex-col ${
        isOpen ? 'w-64' : 'w-20'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
        {isOpen && <h1 className="font-bold text-lg">Fraud Detection</h1>}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="text-sidebar-foreground hover:bg-sidebar-accent"
        >
          {isOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
        </Button>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = currentPage === item.id
          return (
            <button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${
                isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 'hover:bg-sidebar-accent/50'
              }`}
              title={!isOpen ? item.label : ''}
            >
              <Icon size={20} className="flex-shrink-0" />
              {isOpen && <span className="text-sm font-medium">{item.label}</span>}
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        {isOpen && <p className="text-xs text-sidebar-foreground/60">Enterprise Edition</p>}
      </div>
    </div>
  )
}
