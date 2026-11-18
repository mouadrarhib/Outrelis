import axios from 'axios'
import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router'
import { FeedbackAlert } from '../../../components/ui/FeedbackAlert'
import { RadioGroup, RadioGroupItem } from '../../../components/ui/beui/RadioGroup'
import { apiErrorMessage, parseApiError } from '../../../lib/api-error'
import { Icon } from '../../../components/ui/Icon'
import { useAuth } from '../../auth/useAuth'
import { getOnboardingState, saveStartingPath } from '../api/onboarding.api'
import type { StartingPath } from '../onboarding.types'

type Phase = 'loading' | 'ready' | 'load-error' | 'saving'

export function StartingPathPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [choice, setChoice] = useState<StartingPath | ''>('')
  const [phase, setPhase] = useState<Phase>('loading')
  const [message, setMessage] = useState('')
  const [retryVersion, setRetryVersion] = useState(0)
  const controller = useRef<AbortController | null>(null)
  const submitting = useRef(false)

  useEffect(() => {
    document.title = 'Outrelis — Choose your starting path'
  }, [])

  useEffect(() => {
    if (!user) return
    controller.current?.abort()
    const request = new AbortController()
    controller.current = request
    getOnboardingState(request.signal).then((state) => {
      if (request.signal.aborted) return
      if (state.completed) {
        navigate('/account', { replace: true })
        return
      }
      setChoice(state.starting_path ?? '')
      setPhase('ready')
    }).catch((error) => {
      if (request.signal.aborted || axios.isCancel(error)) return
      setMessage(apiErrorMessage(parseApiError(error)))
      setPhase('load-error')
    })
    return () => request.abort()
  }, [navigate, retryVersion, user])

  if (!user) return <Navigate to="/login" replace />

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!choice || submitting.current) return
    submitting.current = true
    setPhase('saving')
    setMessage('')
    const request = new AbortController()
    controller.current = request
    try {
      await saveStartingPath(choice, request.signal)
      if (!request.signal.aborted) navigate('/account', { replace: true })
    } catch (error) {
      if (request.signal.aborted || axios.isCancel(error)) return
      setMessage(apiErrorMessage(parseApiError(error)))
      setPhase('ready')
    } finally {
      submitting.current = false
    }
  }

  async function signOut() {
    if (phase === 'saving') return
    setMessage('')
    try {
      await logout()
      navigate('/login', { replace: true })
    } catch (error) {
      setMessage(apiErrorMessage(parseApiError(error)))
    }
  }

  const loading = phase === 'loading'
  const loadFailed = phase === 'load-error'
  const saving = phase === 'saving'

  return <div className="onboarding-shell">
    <header className="onboarding-header">
      <img src="/outrelis-logo.svg" alt="Outrelis" width="176" height="51" />
      <button className="onboarding-signout" type="button" onClick={signOut} disabled={saving}>
        Sign out
      </button>
    </header>

    <main className="onboarding-main">
      <section className="onboarding-panel" aria-labelledby="starting-path-title" aria-busy={loading || saving}>
        <h1 id="starting-path-title">What would you like to do first?</h1>
        <p className="onboarding-intro">Choose the starting point that fits how you prospect today. You can change it later.</p>

        {loading && <p className="onboarding-loading" role="status">Loading your starting point…</p>}

        {loadFailed && <FeedbackAlert
          open
          tone="error"
          title="Starting point unavailable"
          message={message}
          action={<button className="feedback-action" type="button" onClick={() => {
            setPhase('loading')
            setMessage('')
            setRetryVersion((version) => version + 1)
          }}>Try again</button>}
        />}

        {!loading && !loadFailed && <form className="starting-path-form" onSubmit={submit}>
          <RadioGroup
            value={choice}
            onValueChange={(value) => { setChoice(value as StartingPath); setMessage('') }}
            aria-labelledby="starting-path-title"
            className="path-options"
          >
            <RadioGroupItem
              id="find-first-leads"
              value="find_first_leads"
              label="Find my first leads"
              description="Guide me through choosing a target and building a focused first list."
              className="starting-path-option"
              disabled={saving}
            />
            <RadioGroupItem
              id="grow-pipeline"
              value="grow_pipeline"
              label="Grow my pipeline"
              description="Take me straight to lead search so I can add prospects to an existing process."
              className="starting-path-option"
              disabled={saving}
            />
          </RadioGroup>

          <FeedbackAlert
            open={Boolean(message)}
            tone="error"
            title="Choice not saved"
            message={message}
          />

          <div className="onboarding-action">
            <p>Your choice changes guidance and defaults, not the features available to you.</p>
            <button className="primary onboarding-continue" type="submit" disabled={!choice || saving}>
              <span>{saving ? 'Saving your choice…' : 'Continue'}</span>
              <Icon name="arrow" />
            </button>
          </div>
        </form>}
      </section>
    </main>

    <footer className="onboarding-footer">
      <span>Your first leads.</span>
      <span>Your next opportunities.</span>
    </footer>
  </div>
}
