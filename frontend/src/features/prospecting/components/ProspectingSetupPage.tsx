import axios from 'axios'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import { Navigate, useNavigate } from 'react-router'
import { FeedbackAlert } from '../../../components/ui/FeedbackAlert'
import { Icon } from '../../../components/ui/Icon'
import { Button } from '../../../components/ui/beui/Button'
import { SelectField } from '../../../components/ui/beui/Field'
import { apiErrorMessage, parseApiError } from '../../../lib/api-error'
import { useAuth } from '../../auth/useAuth'
import { getProspectingSetup, saveProspectingSetup } from '../api/prospecting.api'
import type { ProspectingSetupInput } from '../prospecting.types'

type Phase = 'loading' | 'ready' | 'load-error' | 'saving' | 'saved'

const EMPTY_FORM: ProspectingSetupInput = {
  service_name: '', outreach_language: 'en-US', business_category: '',
  locations: [], result_limit_per_location: 20,
}

export function ProspectingSetupPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const reduce = useReducedMotion()
  const [form, setForm] = useState<ProspectingSetupInput>(EMPTY_FORM)
  const [location, setLocation] = useState('')
  const [locationError, setLocationError] = useState('')
  const [preferencesOpen, setPreferencesOpen] = useState(false)
  const [phase, setPhase] = useState<Phase>('loading')
  const [message, setMessage] = useState('')
  const [retryVersion, setRetryVersion] = useState(0)
  const controller = useRef<AbortController | null>(null)
  const submitting = useRef(false)

  useEffect(() => { document.title = 'Outrelis — Prepare your lead search' }, [])

  useEffect(() => {
    if (!user) return
    controller.current?.abort()
    const request = new AbortController()
    controller.current = request
    getProspectingSetup(request.signal).then((setup) => {
      if (request.signal.aborted) return
      if (setup.offer_profile && setup.search_draft) {
        setForm({
          service_name: setup.offer_profile.service_name,
          outreach_language: setup.offer_profile.outreach_language,
          business_category: setup.search_draft.business_category,
          locations: setup.search_draft.locations.map((item) => item.location_query),
          result_limit_per_location: setup.search_draft.result_limit_per_location,
        })
      }
      setPhase('ready')
    }).catch((error) => {
      if (request.signal.aborted || axios.isCancel(error)) return
      setMessage(apiErrorMessage(parseApiError(error)))
      setPhase('load-error')
    })
    return () => request.abort()
  }, [retryVersion, user])

  if (!user) return <Navigate to="/login" replace />

  function update<K extends keyof ProspectingSetupInput>(key: K, value: ProspectingSetupInput[K]) {
    setForm((current) => ({ ...current, [key]: value }))
    setMessage('')
    if (phase === 'saved') setPhase('ready')
  }

  function addLocation() {
    const clean = location.trim().replace(/\s+/g, ' ')
    if (!clean) return setLocationError('Enter a city, state, or region before adding it.')
    if (clean.length > 200) return setLocationError('Keep each location under 200 characters.')
    if (form.locations.some((item) => item.toLocaleLowerCase() === clean.toLocaleLowerCase())) {
      return setLocationError('This location is already included.')
    }
    if (form.locations.length >= 10) return setLocationError('You can search up to 10 locations at a time.')
    update('locations', [...form.locations, clean])
    setLocation('')
    setLocationError('')
  }

  function locationKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key !== 'Enter') return
    event.preventDefault()
    addLocation()
  }

  function removeLocation(index: number) {
    update('locations', form.locations.filter((_, itemIndex) => itemIndex !== index))
    setLocationError('')
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (submitting.current) return
    if (!form.locations.length) return setLocationError('Add at least one location to define your search area.')
    submitting.current = true
    setMessage('')
    setPhase('saving')
    const request = new AbortController()
    controller.current = request
    try {
      const saved = await saveProspectingSetup(form, request.signal)
      if (request.signal.aborted) return
      if (saved.offer_profile && saved.search_draft) {
        setForm({
          service_name: saved.offer_profile.service_name,
          outreach_language: saved.offer_profile.outreach_language,
          business_category: saved.search_draft.business_category,
          locations: saved.search_draft.locations.map((item) => item.location_query),
          result_limit_per_location: saved.search_draft.result_limit_per_location,
        })
      }
      setPhase('saved')
    } catch (error) {
      if (request.signal.aborted || axios.isCancel(error)) return
      setMessage(apiErrorMessage(parseApiError(error)))
      setPhase('ready')
    } finally { submitting.current = false }
  }

  async function signOut() {
    if (phase === 'saving') return
    setMessage('')
    try { await logout(); navigate('/login', { replace: true }) }
    catch (error) { setMessage(apiErrorMessage(parseApiError(error))) }
  }

  const loading = phase === 'loading'
  const loadFailed = phase === 'load-error'
  const saving = phase === 'saving'
  const complete = Boolean(form.service_name.trim() && form.business_category.trim() && form.locations.length)
  const resultEstimate = form.result_limit_per_location
    ? form.result_limit_per_location * form.locations.length : null

  return <div className="onboarding-shell prospecting-shell">
    <header className="onboarding-header prospecting-header">
      <img src="/outrelis-logo.svg" alt="Outrelis" width="176" height="51" />
      <div className="prospecting-header-actions">
        <span>Setup · 2 of 3</span>
        <button className="onboarding-signout" type="button" onClick={signOut} disabled={saving}>Sign out</button>
      </div>
    </header>

    <main className="prospecting-main sentence-main">
      <section className="prospecting-introduction" aria-labelledby="prospecting-title">
        <h1 id="prospecting-title">Tell us what a good lead looks like.</h1>
        <p>Complete one simple search brief. Outrelis will use it to prepare the businesses you want to discover.</p>
      </section>

      <section className="prospecting-workspace" aria-busy={loading || saving}>
        {loading && <div className="prospecting-skeleton" role="status" aria-label="Loading your prospecting setup"><span /><span /><span /><span /></div>}
        {loadFailed && <FeedbackAlert open tone="error" title="Search setup unavailable" message={message}
          action={<button className="feedback-action" type="button" onClick={() => {
            setMessage(''); setPhase('loading'); setRetryVersion((version) => version + 1)
          }}>Try again</button>} />}

        {!loading && !loadFailed && <form className="prospecting-form search-sentence-form" onSubmit={submit}>
          <fieldset className="search-sentence" disabled={saving}>
            <legend className="sr-only">Describe your lead search</legend>
            <label className="sentence-row" htmlFor="service-name">
              <span>I offer</span>
              <input id="service-name" className="sentence-input" placeholder="website design"
                value={form.service_name} onChange={(event) => update('service_name', event.target.value)}
                maxLength={120} autoComplete="organization-title" required />
            </label>
            <label className="sentence-row" htmlFor="business-category">
              <span>and I want to find</span>
              <input id="business-category" className="sentence-input" placeholder="dental clinics"
                value={form.business_category} onChange={(event) => update('business_category', event.target.value)}
                maxLength={150} required />
            </label>
            <div className="sentence-location-block">
              <label className="sentence-row" htmlFor="location">
                <span>in</span>
                <input id="location" className="sentence-input" placeholder="Austin, TX" value={location}
                  onChange={(event) => { setLocation(event.target.value); setLocationError('') }}
                  onKeyDown={locationKeyDown} aria-invalid={Boolean(locationError)}
                  aria-describedby={locationError ? 'location-error' : 'location-help'} maxLength={200} />
              </label>
              <Button variant="secondary" className="location-add" type="button" onClick={addLocation}
                disabled={saving || form.locations.length >= 10}>
                <Icon name="plus" /> Add location
              </Button>
            </div>
            <div className="sentence-location-meta">
              {locationError ? <p className="prospecting-field-error" id="location-error">{locationError}</p>
                : <p id="location-help">Press Enter or add the location. Up to 10 markets.</p>}
              <span>{form.locations.length}/10</span>
            </div>

            <AnimatePresence initial={false}>
              {form.locations.length > 0 && <motion.ul className="location-list" aria-label="Selected locations"
                initial={reduce ? false : { opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {form.locations.map((item, index) => <motion.li key={item.toLocaleLowerCase()} layout
                  initial={reduce ? false : { opacity: 0, y: 8, scale: .97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }} exit={reduce ? undefined : { opacity: 0, y: -5, scale: .98 }}
                  transition={{ duration: .2, ease: [0.2, 0, 0, 1] }}>
                  <Icon name="pin" /><span>{item}</span>
                  <button type="button" onClick={() => removeLocation(index)} aria-label={`Remove ${item}`}><Icon name="close" /></button>
                </motion.li>)}
              </motion.ul>}
            </AnimatePresence>
          </fieldset>

          <motion.div className="search-brief" layout aria-live="polite">
            <div><span>Your target</span><strong>{form.business_category.trim() || 'Not chosen yet'}</strong></div>
            <div><span>Markets</span><strong>{form.locations.length || 'None yet'}</strong></div>
            <div><span>Search capacity</span>
              <AnimatePresence mode="wait" initial={false}><motion.strong key={resultEstimate ?? 'open'}
                initial={reduce ? false : { opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}
                exit={reduce ? undefined : { opacity: 0, y: -4 }} transition={{ duration: .16 }}>
                {resultEstimate ? `Up to ${resultEstimate}` : 'Choose later'}
              </motion.strong></AnimatePresence>
            </div>
          </motion.div>

          <div className="search-preferences">
            <button className="preferences-trigger" type="button" aria-expanded={preferencesOpen}
              aria-controls="search-preferences-panel" onClick={() => setPreferencesOpen((open) => !open)}>
              <span><strong>Search preferences</strong><small>Language and result volume</small></span>
              <motion.svg viewBox="0 0 20 20" aria-hidden="true" animate={{ rotate: preferencesOpen ? 180 : 0 }}
                transition={reduce ? { duration: 0 } : { duration: .2, ease: [0.2, 0, 0, 1] }}><path d="m6 8 4 4 4-4" /></motion.svg>
            </button>
            <AnimatePresence initial={false}>
              {preferencesOpen && <motion.div id="search-preferences-panel" className="preferences-panel"
                initial={reduce ? false : { height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                exit={reduce ? undefined : { height: 0, opacity: 0 }}
                transition={{ duration: reduce ? 0 : .22, ease: [0.2, 0, 0, 1] }}>
                <div className="preferences-grid">
                  <SelectField id="outreach-language" label="Outreach language" value={form.outreach_language}
                    onChange={(event) => update('outreach_language', event.target.value)} disabled={saving}>
                    <option value="en-US">English — United States</option><option value="en">English</option>
                    <option value="es-US">Spanish — United States</option><option value="es">Spanish</option>
                  </SelectField>
                  <SelectField id="result-limit" label="Results per location" value={form.result_limit_per_location ?? ''}
                    onChange={(event) => update('result_limit_per_location', event.target.value ? Number(event.target.value) : null)} disabled={saving}>
                    <option value="10">10 businesses</option><option value="20">20 businesses</option>
                    <option value="50">50 businesses</option><option value="100">100 businesses</option>
                    <option value="">Decide when searching</option>
                  </SelectField>
                </div>
              </motion.div>}
            </AnimatePresence>
          </div>

          <FeedbackAlert open={Boolean(message)} tone="error" title="Setup not saved" message={message} />
          <FeedbackAlert open={phase === 'saved'} tone="success" title="Search prepared"
            message="Your offer, target, and markets are saved. Lead discovery is the next step." />
          <div className="prospecting-submit-row">
            <p>Preparing this brief does not run a search yet.</p>
            <Button type="submit" className="prospecting-submit" disabled={!complete} loading={saving}>
              <span>{saving ? 'Preparing your search…' : phase === 'saved' ? 'Search prepared' : 'Prepare my search'}</span>
              <Icon name={phase === 'saved' ? 'check' : 'arrow'} />
            </Button>
          </div>
        </form>}
      </section>
    </main>
  </div>
}
