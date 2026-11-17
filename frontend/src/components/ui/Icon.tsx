export function Icon({ name }: { name: 'arrow' | 'back' | 'eye' | 'eye-off' }) {
  return <svg className="od-icon" viewBox="0 0 24 24" aria-hidden="true">
    {name === 'arrow' && <path d="M5 12h14m-6-6 6 6-6 6" />}
    {name === 'back' && <path d="M19 12H5m6-6-6 6 6 6" />}
    {(name === 'eye' || name === 'eye-off') && <>
      <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
      {name === 'eye-off' && <path d="m3 3 18 18" />}
    </>}
  </svg>
}
