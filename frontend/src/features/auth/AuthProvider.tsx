import { useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { setAccessToken } from '../../lib/http'
import { currentUser, loginAccount, logoutAccount } from './api/auth.api'
import type { Credentials, User } from './auth.types'

import { AuthContext } from './auth.context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const expiry = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  function clearSession() {
    clearTimeout(expiry.current)
    setAccessToken(null)
    setUser(null)
  }

  useEffect(() => {
    window.addEventListener('outrelis:session-expired', clearSession)
    return () => {
      window.removeEventListener('outrelis:session-expired', clearSession)
      clearTimeout(expiry.current)
      setAccessToken(null)
    }
  }, [])

  async function login(credentials: Credentials, signal: AbortSignal) {
    const result = await loginAccount(credentials, signal)
    signal.throwIfAborted()
    setAccessToken(result.access_token)
    try {
      const profile = await currentUser(signal)
      signal.throwIfAborted()
      setUser(profile)
      clearTimeout(expiry.current)
      expiry.current = setTimeout(clearSession, result.expires_in * 1000)
    } catch (error) {
      clearSession()
      throw error
    }
  }

  async function logout() {
    await logoutAccount()
    clearSession()
  }

  return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>
}

