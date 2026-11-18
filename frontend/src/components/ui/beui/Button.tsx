// Adapted to the Outrelis visual system from beUI motion button patterns.
import { motion, useReducedMotion } from 'motion/react'
import type { HTMLMotionProps } from 'motion/react'
import type { ReactNode } from 'react'
import { SPRING_PRESS } from '../../../lib/beui/ease'

type ButtonProps = Omit<HTMLMotionProps<'button'>, 'children'> & {
  children: ReactNode
  loading?: boolean
  variant?: 'primary' | 'secondary' | 'ghost'
}

export function Button({ children, loading = false, disabled, variant = 'primary', className = '', ...props }: ButtonProps) {
  const reduce = useReducedMotion()

  return <motion.button
    {...props}
    className={`beui-button beui-button-${variant} ${className}`.trim()}
    disabled={disabled || loading}
    aria-busy={loading}
    whileTap={reduce || disabled || loading ? undefined : { scale: 0.985 }}
    transition={SPRING_PRESS}
  >
    {children}
  </motion.button>
}
