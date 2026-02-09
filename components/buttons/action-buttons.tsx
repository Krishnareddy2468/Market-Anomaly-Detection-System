import { Button, ButtonProps } from '@/components/ui/button'
import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface ActionButtonProps extends ButtonProps {
  children: ReactNode
}

export function PrimaryButton({ children, className, ...props }: ActionButtonProps) {
  return (
    <Button
      className={cn('bg-primary hover:bg-primary/90 text-primary-foreground', className)}
      {...props}
    >
      {children}
    </Button>
  )
}

export function DangerButton({ children, className, ...props }: ActionButtonProps) {
  return (
    <Button
      className={cn('bg-destructive hover:bg-destructive/90 text-destructive-foreground', className)}
      {...props}
    >
      {children}
    </Button>
  )
}

export function SecondaryButton({ children, className, ...props }: ActionButtonProps) {
  return (
    <Button
      variant="outline"
      className={cn('border-border hover:bg-secondary', className)}
      {...props}
    >
      {children}
    </Button>
  )
}

export function GhostButton({ children, className, ...props }: ActionButtonProps) {
  return (
    <Button
      variant="ghost"
      className={cn('hover:bg-secondary', className)}
      {...props}
    >
      {children}
    </Button>
  )
}
