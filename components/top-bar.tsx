'use client';

import { Menu, User } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface TopBarProps {
  pageTitle: string
  onMenuToggle: () => void
}

export function TopBar({ pageTitle, onMenuToggle }: TopBarProps) {
  return (
    <div className="sticky top-0 h-16 border-b border-border bg-card flex items-center justify-between px-6 z-30">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={onMenuToggle} className="md:hidden">
          <Menu size={20} />
        </Button>
        <h2 className="text-2xl font-bold text-foreground">{pageTitle}</h2>
      </div>
      <Button variant="ghost" size="icon">
        <User size={20} />
      </Button>
    </div>
  )
}
