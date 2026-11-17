import { createContext } from 'react'
import type { Credentials, User } from './auth.types'

export interface AuthState {
  user: User | null
  login: (credentials: Credentials, signal: AbortSignal) => Promise<void>
  logout: () => Promise<void>
}
export const AuthContext = createContext<AuthState | null>(null)
