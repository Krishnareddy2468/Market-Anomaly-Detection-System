import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface PageContainerProps {
  children: ReactNode
  className?: string
  withPadding?: boolean
}

export function PageContainer({ children, className, withPadding = true }: PageContainerProps) {
  return (
    <div className={cn('flex-1 overflow-auto bg-background', withPadding && 'p-6', className)}>
      <div className="mx-auto max-w-7xl">{children}</div>
    </div>
  )
}
