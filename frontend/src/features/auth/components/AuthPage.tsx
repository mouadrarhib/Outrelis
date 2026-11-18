import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'
import axios from 'axios'
import gsap from 'gsap'
import { FeedbackAlert } from '../../../components/ui/FeedbackAlert'
import { Icon } from '../../../components/ui/Icon'
import { useAuth } from '../useAuth'
import { registerAccount } from '../api/auth.api'
import { authError } from '../auth.errors'
import type { FieldName } from '../auth.errors'

type Mode = 'login' | 'register' | 'recovery'
type Fields = Record<FieldName, string>

// A keyed form keeps password and validation state from leaking between routes.
export function AuthPage({ mode }: { mode: Mode }) {
  const location = useLocation()
  return <AuthForm key={mode + location.key} mode={mode} />
}

function AuthForm({ mode }: { mode: Mode }) {
  const { user, login } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const registration = mode === 'register'
  const recovery = mode === 'recovery'
  const [values, setValues] = useState<Fields>({ email: location.state?.email || '', password: '', full_name: '' })
  const [errors, setErrors] = useState<Partial<Fields>>({})
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const [revealed, setRevealed] = useState(false)
  const root = useRef<HTMLElement>(null)
  const controller = useRef<AbortController | null>(null)
  const submitting = useRef(false)
  const heading = registration ? 'Make room for your next opportunity.' : recovery ? 'Let’s get you back in.' : 'Welcome back.'

  useEffect(() => {
    document.title = `Outrelis — ${registration ? 'Create an account' : recovery ? 'Reset password' : 'Welcome back'}`
    if (location.state?.focus) root.current?.querySelector<HTMLElement>('h1')?.focus({ preventScroll: true })
    const media = gsap.matchMedia()
    media.add('(prefers-reduced-motion: no-preference)', () => {
      if (!root.current) return
      gsap.fromTo(root.current, { y: 8, opacity: 0.65 }, { y: 0, opacity: 1, duration: 0.3, ease: 'power2.out', clearProps: 'transform,opacity' })
    })
    return () => { controller.current?.abort(); media.revert() }
  }, [registration, recovery, location.state])

  if (user) return <Navigate to="/getting-started" replace />

  function validate(field: FieldName, value: string) {
    const length = Array.from(value).length
    if (field === 'full_name') return !value.trim() ? 'Enter your name.' : Array.from(value.trim()).length > 100 ? 'Use no more than 100 characters.' : ''
    if (field === 'email') return !value.trim() ? 'Enter your email address.' : value.trim().length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim()) ? 'Enter a valid email address, such as you@example.com.' : ''
    if (!length) return 'Enter your password.'
    if (registration && length < 8) return 'Use at least 8 characters.'
    return length > 128 ? 'Use no more than 128 characters.' : ''
  }

  function change(field: FieldName, value: string) {
    setValues((current) => ({ ...current, [field]: value }))
    setMessage('')
    if (errors[field]) setErrors((current) => ({ ...current, [field]: validate(field, value) }))
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting.current) return
    const fields: FieldName[] = registration ? ['full_name', 'email', 'password'] : ['email', 'password']
    const nextErrors = Object.fromEntries(fields.map((field) => [field, validate(field, values[field])]))
    setErrors(nextErrors)
    setMessage('')
    const first = fields.find((field) => nextErrors[field])
    if (first) { root.current?.querySelector<HTMLInputElement>(`[name="${first}"]`)?.focus(); return }
    submitting.current = true
    setBusy(true)
    controller.current = new AbortController()
    const signal = controller.current.signal
    try {
      const credentials = { email: values.email.trim(), password: values.password }
      if (registration) {
        await registerAccount({ ...credentials, full_name: values.full_name.trim() }, signal)
        if (!signal.aborted) navigate('/login', { replace: true, state: { email: credentials.email, registered: true, focus: true } })
      } else {
        await login(credentials, signal)
        if (!signal.aborted) navigate('/getting-started', { replace: true })
      }
    } catch (error) {
      if (signal.aborted || axios.isCancel(error)) return
      const feedback = authError(error, registration)
      setMessage(feedback.message)
      if (feedback.fields) setErrors(feedback.fields)
    } finally {
      if (!signal.aborted) { setBusy(false); submitting.current = false }
    }
  }

  function input(field: FieldName, label: string) {
    const id = `${mode}-${field}`
    const password = field === 'password'
    return <div className="field">
      <label htmlFor={id}>{label}</label>
      <div className={password ? 'password-row' : undefined}>
        <input id={id} name={field} type={password ? (revealed ? 'text' : 'password') : field === 'email' ? 'email' : 'text'}
          autoComplete={password ? (registration ? 'new-password' : 'current-password') : field === 'full_name' ? 'name' : 'email'}
          inputMode={field === 'email' ? 'email' : undefined} autoCapitalize={field === 'email' ? 'none' : undefined}
          spellCheck={field === 'full_name'} placeholder={field === 'email' ? 'you@yourbusiness.com' : field === 'full_name' ? 'Your name' : undefined}
          value={values[field]} onChange={(event) => change(field, event.target.value)} disabled={busy} required
          aria-invalid={!!errors[field]} aria-describedby={`${id}-error${password && registration ? ' password-requirements' : ''}`}
          onBlur={() => { if (values[field] || errors[field]) setErrors((current) => ({ ...current, [field]: validate(field, values[field]) })) }} />
        {password && <button className="reveal" type="button" aria-label={revealed ? 'Hide password' : 'Show password'}
          aria-pressed={revealed} aria-controls={id} onClick={() => setRevealed(!revealed)}>
          <Icon name={revealed ? 'eye-off' : 'eye'} />
        </button>}
      </div>
      <p className="error" id={`${id}-error`} hidden={!errors[field]}>{errors[field]}</p>
    </div>
  }

  const linkState = { email: values.email, focus: true }
  return <section className="view" ref={root} aria-labelledby={`${mode}-title`}>
    {recovery && <Link className="text-link back" to="/login" state={linkState}><Icon name="back" />Back to sign in</Link>}
    <h1 id={`${mode}-title`} tabIndex={-1}>{heading}</h1>
    <p className="intro">{registration ? 'Start with a little about yourself.' : recovery ? 'Password recovery is coming soon.' : 'Your next opportunity is waiting.'}</p>
    {recovery ? <p className="helper recovery-note">Password recovery isn’t available yet. Return to sign in to try your password again.</p> : <>
      <div className="feedback-slot success-notice">
        <FeedbackAlert
          open={Boolean(location.state?.registered)}
          tone="success"
          title="Your account is ready."
          message="Sign in to continue."
        />
      </div>
      <form className="auth-form" onSubmit={submit} noValidate aria-busy={busy}>
        {registration && input('full_name', 'Full name')}
        {input('email', 'Email address')}
        {input('password', 'Password')}
        {registration && <p className="requirements" id="password-requirements">Use 8–128 characters. A longer passphrase works well.</p>}
        {!registration && <div className="forgot-row"><Link className="text-link" to="/forgot-password" state={linkState}>Forgot password?</Link></div>}
        <FeedbackAlert
          open={Boolean(message)}
          tone="error"
          title={registration ? 'Account not created' : 'Sign-in failed'}
          message={message}
        />
        <button type="submit" className="primary" disabled={busy}><span>{busy ? (registration ? 'Creating account…' : 'Signing in…') : registration ? 'Create account' : 'Sign in'}</span><Icon name="arrow" /></button>
      </form>
      <p className="switch">{registration ? 'Already have an account?' : 'New to Outrelis?'} <Link className="text-link" to={registration ? '/login' : '/register'} state={linkState}>{registration ? 'Sign in' : 'Create an account'}</Link></p>
      <p className="status-line" role="status" aria-live="polite">{busy ? 'Please wait…' : ''}</p>
    </>}
  </section>
}
