'use client';

import { Menu, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useCurrency } from '@/lib/contexts/currency-context'

interface TopBarProps {
  pageTitle: string
  onMenuToggle: () => void
}

export function TopBar({ pageTitle, onMenuToggle }: TopBarProps) {
  const { currency, setCurrency } = useCurrency()

  return (
    <div className="sticky top-0 h-16 border-b border-border bg-card flex items-center justify-between px-6 z-30">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={onMenuToggle} className="md:hidden">
          <Menu size={20} />
        </Button>
        <h2 className="text-2xl font-bold text-foreground">{pageTitle}</h2>
      </div>
      <div className="flex items-center gap-3">
        <Select value={currency} onValueChange={(value) => setCurrency(value as 'INR' | 'USD' | 'EUR')}>
          <SelectTrigger className="w-28 h-9">
            <SelectValue placeholder="Currency" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="INR">INR</SelectItem>
            <SelectItem value="USD">USD</SelectItem>
            <SelectItem value="EUR">EUR</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="ghost" size="icon">
          <User size={20} />
        </Button>
      </div>
    </div>
  )
}
