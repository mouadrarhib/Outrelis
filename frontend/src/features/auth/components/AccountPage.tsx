import { useEffect, useState } from 'react'
import { Navigate } from 'react-router'
import { useAuth } from '../useAuth'
import { authError } from '../auth.errors'
import { Icon } from '../../../components/ui/Icon'

export function AccountPage() {
  const { user, logout } = useAuth()
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  useEffect(() => { document.title = 'Outrelis — Your account' }, [])
  if (!user) return <Navigate to="/login" replace />
  async function signOut() {
    setBusy(true)
    setMessage('')
    try { await logout() } catch (error) { setMessage(authError(error).message); setBusy(false) }
  }
  return <section className="view" aria-labelledby="account-title">
    <h1 id="account-title">You’re signed in.</h1>
    <p className="intro">Welcome{user.full_name ? `, ${user.full_name}` : ' back'}.</p>
    <dl className="account-details"><dt>Email address</dt><dd>{user.email}</dd></dl>
    {message && <p className="summary" role="alert">{message}</p>}
    <button className="primary" type="button" onClick={signOut} disabled={busy}><span>{busy ? 'Signing out…' : 'Sign out'}</span><Icon name="arrow" /></button>
  </section>
}
