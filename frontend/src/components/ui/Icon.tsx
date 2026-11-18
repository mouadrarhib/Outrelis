type IconName = 'arrow' | 'back' | 'check' | 'close' | 'eye' | 'eye-off' | 'pin' | 'plus'

export function Icon({ name }: { name: IconName }) {
  return <svg className="od-icon" viewBox="0 0 24 24" aria-hidden="true">
    {name === 'arrow' && <path d="M5 12h14m-6-6 6 6-6 6" />}
    {name === 'back' && <path d="M19 12H5m6-6-6 6 6 6" />}
    {name === 'check' && <path d="m5 12 4 4L19 6" />}
    {name === 'close' && <path d="m6 6 12 12M18 6 6 18" />}
    {name === 'plus' && <path d="M12 5v14M5 12h14" />}
    {name === 'pin' && <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /></>}
    {(name === 'eye' || name === 'eye-off') && <>
      <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
      {name === 'eye-off' && <path d="m3 3 18 18" />}
    </>}
  </svg>
}
