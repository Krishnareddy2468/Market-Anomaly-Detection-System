'use client';

import { useEffect, useState } from 'react'
import { Menu, User, Bell, Moon, Sun, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useCurrency } from '@/lib/contexts/currency-context'
import { useTheme } from 'next-themes'

interface TopBarProps {
  pageTitle: string
  onMenuToggle: () => void
}

/** Live clock that ticks every second. Renders nothing until mounted to
 *  avoid a server/client hydration mismatch. */
function LiveClock() {
  const [now, setNow] = useState<Date | null>(null)

  useEffect(() => {
    setNow(new Date())
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  if (!now) {
    // Reserve space so layout doesn't shift when the clock appears.
    return <div className="hidden md:block w-[168px] h-9" aria-hidden />
  }

  const date = now.toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' })
  const time = now.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true })

  return (
    <div
      className="hidden md:flex items-center gap-1.5 rounded-lg border border-border bg-muted/40 px-2.5 h-9 text-xs text-muted-foreground"
      title="Current local time"
    >
      <Clock size={14} className="text-muted-foreground" />
      <span className="font-medium text-foreground">{time}</span>
      <span className="text-muted-foreground/70">·</span>
      <span>{date}</span>
    </div>
  )
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
        <h2 className="text-lg font-semibold text-foreground">{pageTitle}</h2>
        <span
          title="Demonstration instance running on seeded sample data"
          className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-[11px] font-medium leading-none text-amber-600 dark:text-amber-400"
        >
          <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
          Demo Environment
        </span>
      </div>
      <div className="flex items-center gap-2">
        <LiveClock />
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
