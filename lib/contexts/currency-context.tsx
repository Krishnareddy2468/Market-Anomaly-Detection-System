'use client'

import { createContext, useContext, useEffect, useMemo, useState } from 'react'

export type SupportedCurrency = 'INR' | 'USD' | 'EUR'

interface CurrencyContextValue {
  currency: SupportedCurrency
  setCurrency: (currency: SupportedCurrency) => void
}

const CurrencyContext = createContext<CurrencyContextValue | undefined>(undefined)
const CURRENCY_STORAGE_KEY = 'display_currency'

export function CurrencyProvider({
  children,
  defaultCurrency = 'INR',
}: {
  children: React.ReactNode
  defaultCurrency?: SupportedCurrency
}) {
  const [currency, setCurrency] = useState<SupportedCurrency>(defaultCurrency)

  useEffect(() => {
    const stored = window.localStorage.getItem(CURRENCY_STORAGE_KEY)
    if (stored === 'INR' || stored === 'USD' || stored === 'EUR') {
      setCurrency(stored)
    }
  }, [])

  useEffect(() => {
    window.localStorage.setItem(CURRENCY_STORAGE_KEY, currency)
  }, [currency])

  const value = useMemo(() => ({ currency, setCurrency }), [currency])

  return <CurrencyContext.Provider value={value}>{children}</CurrencyContext.Provider>
}

export function useCurrency(): CurrencyContextValue {
  const context = useContext(CurrencyContext)
  if (!context) {
    throw new Error('useCurrency must be used within CurrencyProvider')
  }
  return context
}
