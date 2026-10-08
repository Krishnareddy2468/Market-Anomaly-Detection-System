'use client';

import { Menu, User, Bell, Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useCurrency } from '@/lib/contexts/currency-context'
import { useTheme } from 'next-themes'

interface TopBarProps {
  pageTitle: string
  onMenuToggle: () => void
}

export function TopBar({ pageTitle, onMenuToggle }: TopBarProps) {
  const { currency, setCurrency } = useCurrency()
  const { theme, setTheme } = useTheme()

  return (
    <div className="sticky top-0 h-16 border-b border-border bg-card/80 backdrop-blur-md flex items-center justify-between px-6 z-30">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={onMenuToggle} className="md:hidden h-9 w-9">
          <Menu size={18} />
        </Button>
        <div>
          <h2 className="text-lg font-semibold text-foreground">{pageTitle}</h2>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Select value={currency} onValueChange={(value) => setCurrency(value as 'INR' | 'USD' | 'EUR')}>
          <SelectTrigger className="w-24 h-9 text-xs font-medium border-border">
            <SelectValue placeholder="Currency" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="INR">₹ INR</SelectItem>
            <SelectItem value="USD">$ USD</SelectItem>
            <SelectItem value="EUR">€ EUR</SelectItem>
          </SelectContent>
        </Select>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 text-muted-foreground hover:text-foreground"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </Button>
        <Button variant="ghost" size="icon" className="relative h-9 w-9 text-muted-foreground hover:text-foreground">
          <Bell size={16} />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive" />
        </Button>
        <div className="h-9 w-9 rounded-full bg-primary/10 flex items-center justify-center">
          <User size={16} className="text-primary" />
        </div>
      </div>
    </div>
  )
}
