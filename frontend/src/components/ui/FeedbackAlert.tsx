import type { ReactNode } from 'react'
import {
  Alert,
  AlertAction,
  AlertClose,
  AlertContent,
  AlertDescription,
  AlertIcon,
  AlertTitle,
} from './beui/Alert'

type FeedbackTone = 'error' | 'success' | 'warning' | 'info'

interface FeedbackAlertProps {
  open: boolean
  tone: FeedbackTone
  title: string
  message: string
  action?: ReactNode
  onDismiss?: () => void
}

export function FeedbackAlert({
  open,
  tone,
  title,
  message,
  action,
  onDismiss,
}: FeedbackAlertProps) {
  const variant = tone === 'error' ? 'destructive' : tone
  return <Alert
    open={open}
    variant={variant}
    className="outrelis-feedback"
    onOpenChange={(next) => { if (!next) onDismiss?.() }}
  >
    <AlertIcon />
    <AlertContent>
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
      {action && <AlertAction>{action}</AlertAction>}
    </AlertContent>
    {onDismiss && <AlertClose />}
  </Alert>
}
