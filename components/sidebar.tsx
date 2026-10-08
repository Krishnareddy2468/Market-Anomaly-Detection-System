'use client';

import { ChevronLeft, ChevronRight, LayoutDashboard, AlertCircle, Search, TrendingUp, History, Settings, Shield } from 'lucide-react'
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
      className={`fixed left-0 top-0 bottom-0 bg-[#0f172a] text-white transition-all duration-300 ease-in-out z-40 flex flex-col border-r border-white/10 ${
        isOpen ? 'w-64' : 'w-[72px]'
      }`}
    >
      {/* Header / Logo */}
      <div className={`flex items-center h-16 border-b border-white/10 ${isOpen ? 'px-5' : 'px-3 justify-center'}`}>
        {isOpen ? (
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-white">
              <Shield className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-tight text-white">Fraud Detection</span>
              <span className="text-[10px] text-white/50 font-medium tracking-widest uppercase">Enterprise</span>
            </div>
          </div>
        ) : (
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-white">
            <Shield className="h-5 w-5" />
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className={`flex-1 py-4 space-y-1 ${isOpen ? 'px-3' : 'px-2'}`}>
        {isOpen && (
          <p className="text-[10px] font-semibold tracking-widest uppercase text-white/40 px-3 mb-3">
            Navigation
          </p>
        )}
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = currentPage === item.id
          return (
            <button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              className={`relative w-full flex items-center gap-3 rounded-lg transition-all duration-200 ${
                isOpen ? 'px-3 py-2.5' : 'px-0 py-2.5 justify-center'
              } ${
                isActive
                  ? 'bg-blue-600/20 text-blue-400 shadow-sm'
                  : 'text-white/80 hover:text-white hover:bg-white/10'
              }`}
              title={!isOpen ? item.label : ''}
            >
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full bg-blue-500" />
              )}
              <Icon size={20} className="flex-shrink-0" />
              {isOpen && <span className="text-sm font-medium">{item.label}</span>}
            </button>
          )
        })}
      </nav>

      {/* Toggle & Footer */}
      <div className={`border-t border-white/10 p-3 ${!isOpen ? 'flex justify-center' : ''}`}>
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="text-white/50 hover:text-white hover:bg-white/10 h-8 w-8"
        >
          {isOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </Button>
      </div>
    </div>
  )
}
